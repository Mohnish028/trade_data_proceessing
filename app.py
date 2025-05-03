from flask import Flask, request, send_file, render_template
import pandas as pd
import re
from io import BytesIO
import os
import traceback
import json
from openpyxl import Workbook
from openpyxl.styles import Font

app = Flask(__name__)

if not os.path.exists('processed_files'):
    os.makedirs('processed_files')

def extract_base_symbol(symbol):
    try:
        matches = re.findall(r'^[A-Z]+', str(symbol))
        return matches[0] if matches else symbol
    except Exception:
        return symbol

def find_header_row(df):
    required_columns = ['Symbol', 'Realized P&L', 'Unrealized P&L']
    for index in range(len(df)):
        row = df.iloc[index].astype(str).str.strip()
        if all(col in row.values for col in required_columns):
            return index
    return None

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
                return render_template('error.html', message="Excel file missing required columns.")

            file.seek(0)
            df = pd.read_excel(file, header=header_row)

            # Remove sensitive fields before processing
            sensitive_fields = ['Account Number', 'Client Name', 'Email', 'Phone']
            df = df.drop(columns=[col for col in sensitive_fields if col in df.columns])
            df.columns = df.columns.str.strip()

            df['Base Symbol'] = df['Symbol'].apply(extract_base_symbol)

            result = df.groupby('Base Symbol').agg({
                'Realized P&L': 'sum',
                'Unrealized P&L': 'sum'
            }).reset_index()

            result['Total P&L'] = result['Realized P&L'] + result['Unrealized P&L']
            result.rename(columns={'Base Symbol': 'Symbol'}, inplace=True)

            breakdown_data = {}
            for base_symbol, group in df.groupby('Base Symbol'):
                breakdown_data[base_symbol] = group[['Symbol', 'Realized P&L', 'Unrealized P&L']].to_dict(orient='records')

            return render_template('display.html', table_data=result.to_dict(orient='records'), breakdown=breakdown_data)

        except Exception as e:
            print("ERROR:", e)
            traceback.print_exc()
            return render_template('error.html', message="Something went wrong. Please upload a correct Excel file.")

    return render_template('upload.html')

@app.route('/save', methods=['POST'])
def save_changes():
    try:
        edited_data = json.loads(request.form.get('editedData', '[]'))

        df = pd.DataFrame(edited_data)
        df['Total P&L'] = df['Realized'] + df['Unrealized']
        df.rename(columns={
            'Symbol': 'Symbol',
            'Realized': 'Realized P&L',
            'Unrealized': 'Unrealized P&L'
        }, inplace=True)

        from openpyxl import Workbook
        from openpyxl.styles import Font

        wb = Workbook()
        ws = wb.active
        ws.title = "Updated Trades"

        header = ['Symbol', 'Realized P&L', 'Unrealized P&L', 'Total P&L']
        ws.append(header)
        for cell in ws[1]:
            cell.font = Font(bold=True)
        # Set nice column widths
        column_widths = [20, 18, 20, 15]
        for i, width in enumerate(column_widths, start=1):
         ws.column_dimensions[chr(64 + i)].width = width
        for _, row in df.iterrows():
            ws.append([row['Symbol'], row['Realized P&L'], row['Unrealized P&L'], row['Total P&L']])

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name='updated_trades.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print("Error in /save route:", e)
        return render_template('error.html', message="Failed to save changes.")


if __name__ == '__main__':
    app.run(debug=True)
