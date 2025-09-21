Payslip Extractor Pro
Overview

Payslip Extractor Pro is a Streamlit-based web application that extracts payroll information from scanned or digital payslip files (PDF or image format) using OCR (Optical Character Recognition). It identifies key data fields such as employee name, bank details, net pay, and pay date, then compiles this information into structured Excel reports grouped by bank.

This tool is ideal for finance teams, HR departments, and payroll processors who need to automate the extraction and consolidation of payslip data from non-editable sources.

Key Features

Upload multiple files in PDF, JPG, PNG, or JPEG format

Automatically extract fields using OCR and pattern recognition

Supports standard fields: Employee Name, Account Number, Bank, Net Pay, Pay Date

Bank name standardization (e.g., "United Bank for Africa" → "UBA")

Confidence scoring for OCR quality

Inline editing of extracted data

Detects and warns about duplicate account numbers

Saves data to separate Excel files per bank

Dashboard summarizing total net pay and number of payslips per bank

Download ready-to-use Excel files for each bank

Technologies Used

Streamlit – for building the interactive web interface

pytesseract – for OCR text extraction

Pillow – for image processing and handling

OpenCV (opencv-python) – for image preprocessing (e.g., grayscale, thresholding)

NumPy – for array operations and numerical tasks

Pandas – for data handling, transformation, and Excel output

openpyxl – for working with .xlsx Excel files

opencv-python-headless – used for server environments without GUI support

pdf2image – for converting PDFs into images that can be processed via OCR

Installation
1. Clone the Repository
git clone https://github.com/dlifeofjay/Payslip.git
cd Payslip

2. Set Up a Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate    # On Windows use: venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Install Tesseract-OCR

Make sure Tesseract OCR
 is installed and accessible in your system’s PATH.

Ubuntu

sudo apt update
sudo apt install tesseract-ocr


Windows
Download the installer from GitHub Releases
 and add the installation path (e.g., C:\Program Files\Tesseract-OCR) to your system environment variables.

Running the App
streamlit run app.py


This will launch a local web interface in your browser.

How to Use

Upload Files
Upload one or more payslip files in PDF or image formats (JPEG, PNG).

OCR and Extraction
The app uses Tesseract to extract text and identify relevant fields using regex patterns.

Review Extracted Data
Review the parsed data in a table. Edit values inline if necessary. Duplicate account numbers will be flagged.

Confirm and Save
After confirming the data, it will be saved to Excel files organized by bank.

Download Payslip Data
Download Excel files for each bank directly from the interface.

Output Example

For each bank, a file will be created in the bank_payslips/ directory:

bank_payslips/
├── payslip_UBA.xlsx
├── payslip_FirstBank.xlsx
└── payslip_GTBank.xlsx


Each file contains fields like:

Employee Name

Account Number

Bank

Net Pay

Pay Date

Confidence (OCR)

Source File

Customization

You can customize:

Regex patterns in the parse_fields function to suit your payslip layout

Bank name aliases for additional banks

Fields extracted from the OCR text

Excel saving logic, including adding timestamps or batch tags
