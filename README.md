# Trade Processor Web App

This is a Flask-based web application that allows users to upload an Excel file containing trade data, processes it, and provides the result for download.

## Features
- Upload Excel files (.xlsx, .xls)
- Check for required columns (Symbol, Realized P&L, Unrealized P&L)
- Display processed data on webpage
- Download the processed Excel file
- Handles wrong file types and missing columns

## How to Run
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python app.py`
4. Visit `http://127.0.0.1:5000/` in your browser

---
