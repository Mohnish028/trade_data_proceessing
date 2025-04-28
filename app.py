from flask import Flask, request, send_file, render_template
import pandas as pd
import re
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import os

# Initialize Flask app
app = Flask(__name__)

# Create a folder to save processed files
if not os.path.exists('processed_files'):
    os.makedirs('processed_files')

# Function to extract base symbol
def extract_base_symbol(symbol):
    try:
        matches = re.findall(r'^[A-Z]+', str(symbol))
        return matches[0] if matches else symbol
    except Exception:
        return symbol

# Function to find header row
def find_header_row(df):
    required_columns = ['Symbol', 'Realized P&L', 'Unrealized P&L']
    for index in range(len(df)):
        row = df.iloc[index].astype(str).str.strip()
        if all(col in row.values for col in required_columns):
            return index
    return None

# Home route to upload and process file
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            return render_template('error.html', message="No file uploaded. Please upload an Excel file.")

        file = request.files['file']

        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            return render_template('error.html', message="Wrong file type. Please upload only .xlsx or .xls Excel file.")

        try:
            temp_df = pd.read_excel(file, header=None)
            header_row = find_header_row(temp_df)

            if header_row is None:
                return render_template('error.html', message="Excel file missing required columns: Symbol, Realized P&L, Unrealized P&L.")

            file.seek(0)
            df = pd.read_excel(file, header=header_row)
            df.columns = df.columns.str.strip()

            # Process data
            df['Base Symbol'] = df['Symbol'].apply(extract_base_symbol)
            result = df.groupby('Base Symbol').agg({
                'Realized P&L': 'sum',
                'Unrealized P&L': 'sum'
            }).reset_index()
            result['Total P&L'] = result['Realized P&L'] + result['Unrealized P&L']
            result.rename(columns={'Base Symbol': 'Symbol'}, inplace=True)

            # Save processed file to disk
            output_path = os.path.join('processed_files', 'processed_trades.xlsx')
            result.to_excel(output_path, index=False, engine='openpyxl')

            # Format the Excel file
            workbook = load_workbook(output_path)
            worksheet = workbook.active

            for column_cells in worksheet.columns:
                length = max(len(str(cell.value or "")) for cell in column_cells)
                worksheet.column_dimensions[get_column_letter(column_cells[0].column)].width = length + 2

            last_row = worksheet.max_row + 1
            worksheet[f'A{last_row}'] = "TOTAL"
            worksheet[f'D{last_row}'] = f"=SUM(D2:D{last_row-1})"

            workbook.save(output_path)

            # Render table for display
            table_html = result.to_html(classes='data')
            return render_template('display.html', table=table_html)

        except Exception:
            return render_template('error.html', message="Something went wrong. Please upload a correct Excel file.")

    return render_template('upload.html')

# Route to download the processed file
@app.route('/download')
def download_file():
    output_path = os.path.join('processed_files', 'processed_trades.xlsx')

    if not os.path.exists(output_path):
        return render_template('error.html', message="No file available. Please upload and process a file first.")

    return send_file(
        output_path,
        as_attachment=True,
        download_name='processed_trades.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Run the app
if __name__ == '__main__':
    app.run(debug=True)