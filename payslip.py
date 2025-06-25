import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import re
import pytesseract
import cv2
from pdf2image import convert_from_bytes
from PIL import Image
from datetime import datetime

# 🛠 Setup
SAVE_DIR = "bank_payslips"
os.makedirs(SAVE_DIR, exist_ok=True)

st.set_page_config(page_title="Payslip Extractor Pro", page_icon="💼")
st.title("💼 Payslip Extractor Pro - Enhanced")

uploaded_files = st.file_uploader("📎 Upload Payslips (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)

COLUMN_ALIASES = {
    "Account Number": ["acct no", "account number", "acc number", "acc no"],
    "Bank": ["bank", "bank name"],
    "Employee Name": ["employee name", "name", "staff name"],
    "Net Pay": ["net pay", "amount paid", "salary", "gross"],
    "Pay Date": ["date", "payment date", "pay date"]
}
BANK_NAME_ALIASES = {
    "UBA": ["united bank of africa", "uba bank", "united bank", "uba", "united bank for africa"],
    "FirstBank": ["first bank", "firstbank", "first bank nigeria", "fbn"],
    "GTBank": ["gt bank", "guaranty trust bank", "gtb", "gtbank"],
    "AccessBank": ["access bank", "accessbank", "access"],
    "ZenithBank": ["zenith bank", "zenithbank", "zenith"],
    "FidelityBank": ["fidelity", "fid", "fidelity bank"],
    "Stanbic IBTC": ["stanbic", "stanbic bank"],
    "UnionBank": ["union", "union bank", "unionbank"],
    "WemaBank": ["wema", "wema bank", "wemanigeria"],
    "SterlingBank": ["sterling", "sterling bank", "sterling nigeria"],
    "EcoBank": ["eco", "eco bank", "eco nigeria"]
}

def standardize_bank_name(name):
    if not name: return ""
    name = name.lower().strip()
    for standard, aliases in BANK_NAME_ALIASES.items():
        if name in aliases:
            return standard
    return name.title()

def clean_amount(val):
    if not val: return ""
    val = val.replace(",", "").replace("₦", "").strip()
    try:
        num = float(val)
        if num < 100:
            num *= 1000
        return f"{num:,.2f}"
    except:
        return val

def extract_text_and_confidence(img):
    data = pytesseract.image_to_data(img, config="--psm 6", output_type=pytesseract.Output.DICT)
    words = data.get("text", [])
    confs = data.get("conf", [])

    valid_confs = []
    for c in confs:
        try:
            score = float(c)
            if score > 0:
                valid_confs.append(score)
        except:
            continue

    text = " ".join(w for w in words if w.strip())
    avg_conf = np.mean(valid_confs) if valid_confs else 0
    return text, round(avg_conf, 1)

def preprocess_image(image_bytes):
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return thresh

def parse_fields(text):
    patterns = {
        "Employee Name": r"(?i)(?:employee name|name)[^\w]{0,5}([A-Za-z .'-]+)",
        "Account Number": r"(?i)(?:acct no|account number|acc no)[^\d]{0,5}([\d]{6,})",
        "Bank": r"(?i)(?:bank name|bank)[^\w]{0,5}([A-Za-z &]+)",
        "Net Pay": r"(?i)(?:net\s*pay|amount paid|salary|gross)[^\d]{0,5}([\d,\.]+)",
        "Pay Date": r"(?i)(?:date|pay date|payment date)[^\d]{0,5}([\d/\-.]+)"
    }
    result = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            val = match.group(1).strip()
            if key == "Net Pay":
                result[key] = clean_amount(val)
            elif key == "Bank":
                result[key] = standardize_bank_name(val)
            else:
                result[key] = val
        else:
            result[key] = ""
    return result

def load_existing(bank):
    path = os.path.join(SAVE_DIR, f"payslip_{bank}.xlsx")
    if os.path.exists(path):
        return pd.read_excel(path)
    return pd.DataFrame()

def save_bank_data(bank, df):
    path = os.path.join(SAVE_DIR, f"payslip_{bank}.xlsx")
    df.to_excel(path, index=False, engine="openpyxl")

# 🧠 Initialize session
if "batch_data" not in st.session_state:
    st.session_state.batch_data = []

# 🔍 Process files
if uploaded_files:
    for file in uploaded_files:
        file_bytes = file.read()
        pages = []
        if file.type == "application/pdf":
            for page in convert_from_bytes(file_bytes):
                buf = io.BytesIO()
                page.save(buf, format="PNG")
                pages.append(preprocess_image(buf.getvalue()))
        else:
            pages.append(preprocess_image(file_bytes))

        for img in pages:
            text, conf = extract_text_and_confidence(img)
            data = parse_fields(text)
            data["Confidence"] = conf
            data["Source File"] = file.name
            st.session_state.batch_data.append(data)

# 🧾 Review and Confirmation
st.subheader("🔍 Review & Confirm Extracted Payslips")
if st.session_state.batch_data:
    editable_df = pd.DataFrame(st.session_state.batch_data)
    edited_df = st.data_editor(editable_df, key="editor", num_rows="dynamic", use_container_width=True)

    if st.button("✅ Confirm All Payslips"):
        df = edited_df.copy()
        if df["Account Number"].duplicated().any():
            st.warning("⚠️ Duplicate Account Numbers found. Please resolve them before proceeding.")
        else:
            summary = df.groupby("Bank").agg(
                Payslips=("Account Number", "count"),
                TotalNetPay=("Net Pay", lambda x: sum(float(str(v).replace(",", "")) for v in x if str(v).replace(",", "").replace(".", "").isdigit()))
            ).reset_index()

            st.subheader("📊 Summary Dashboard")
            st.dataframe(summary)

            for bank, bank_df in df.groupby("Bank"):
                old = load_existing(bank)
                combined = pd.concat([old, bank_df], ignore_index=True).drop_duplicates(subset=["Account Number"], keep="last")
                save_bank_data(bank, combined)
                st.success(f"✅ Saved {len(bank_df)} records to `{bank}`")

# ⬇️ Export
st.subheader("⬇️ Download Payslips by Bank")
for file in os.listdir(SAVE_DIR):
    if file.endswith(".xlsx"):
        label = file.replace("payslip_", "").replace(".xlsx", "").title()
        with open(os.path.join(SAVE_DIR, file), "rb") as f:
            st.download_button(
                label=f"Download {label} Payslips",
                data=f,
                file_name=file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

