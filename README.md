# Trade Data Processing Web App 📊

This is a Flask-based web application for uploading, editing, grouping, and exporting trade data from Excel files. Designed to be simple and user-friendly, it helps users analyze trades by base symbol and export clean, formatted summaries.

---

## Features

-  Upload `.xlsx` or `.xls` Excel files
-  Automatically detects the correct header row
-  Groups trades by **base symbol** (e.g., NIFTY, HCLTECH)
-  Inline editing of Realized and Unrealized P&L
-  Auto-recalculates **Total P&L**
-  Exports clean, formatted Excel summary
-  Supports full pagination with DataTables
-  Easy-to-use UI with Bootstrap modals for original symbol details

---

##  Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Bootstrap, DataTables.js
- **Excel Handling:** `pandas`, `openpyxl`

---

## How to Use

1. Clone the repo:
    
    git clone https://github.com/Mohnish028/trade_data_proceessing.git
    cd trade_data_proceessing
    

2. Create a virtual environment:
    
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    

3. Install requirements:
    
    pip install -r requirements.txt
    

4. Run the app:
    
    python app.py
    

5. Open your browser and go to:
    
    http://127.0.0.1:5000/
    

---

## 📦 Output Example

- Clean Excel export with columns:

