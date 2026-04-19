from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io
import chardet
from faker import Faker
import random

app = Flask(__name__)
CORS(app)
fake = Faker()

def detect_encoding(file_bytes, sample_size=10000):
    """Detect file encoding, fallback to latin-1 for files chardet detects as ascii/iso-8859-1"""
    result = chardet.detect(file_bytes[:sample_size])
    detected = result['encoding'] or 'utf-8'
    if detected.lower() in ('ascii', 'iso-8859-1', 'windows-1252'):
        return 'latin-1'
    return detected


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/process', methods=['POST'])
def process_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        file_bytes = file.read()
        encoding = detect_encoding(file_bytes)
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
        
        if 'Precinct Split' not in df.columns:
            return jsonify({'error': 'CSV must have a "Precinct Split" column'}), 400
        
        def add_sequence(group):
            group = group.copy()
            n = len(group)
            group['Updated Precinct Split Code'] = [
                f"{code}_{str(i).zfill(3)}" for code, i in zip(group['Precinct Split'], range(1, n + 1))
            ]
            group['Start Page'] = [(i - 1) * 2 + 1 for i in range(1, n + 1)]
            group['End Page'] = [i * 2 for i in range(1, n + 1)]
            return group
        
        df = df.groupby('Precinct Split', group_keys=False).apply(add_sequence)
        df = df.sort_index().reset_index(drop=True)
        
        # Continuous page numbers across all rows
        total = len(df)
        df['Start Page'] = [(i - 1) * 2 + 1 for i in range(1, total + 1)]
        df['End Page'] = [i * 2 for i in range(1, total + 1)]
        
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='updated_precinct_split.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


FAKE_PROVIDERS = {
    'firstname': lambda: fake.first_name(),
    'lastname': lambda: fake.last_name(),
    'fname': lambda: fake.first_name_male() if random.random() > 0.5 else fake.first_name_female(),
    'fullname': lambda: fake.name(),
    'name': lambda: fake.name(),
    'email': lambda: fake.email(),
    'phone': lambda: fake.phone_number(),
    'address': lambda: fake.street_address(),
    'street': lambda: fake.street_name(),
    'city': lambda: fake.city(),
    'state': lambda: fake.state(),
    'zip': lambda: fake.zip_code(),
    'zipcode': lambda: fake.zip_code(),
    'country': lambda: fake.country(),
    'company': lambda: fake.company(),
    'job': lambda: fake.job(),
    'ssn': lambda: fake.ssn(),
    'date': lambda: fake.date(),
    'datetime': lambda: fake.date_time(),
    'time': lambda: fake.time(),
    'url': lambda: fake.url(),
    'username': lambda: fake.user_name(),
    'password': lambda: fake.password(),
    'ipv4': lambda: fake.ipv4(),
    'ipv6': lambda: fake.ipv6(),
    'mac': lambda: fake.mac_address(),
    'license': lambda: fake.license_plate(),
    'latitude': lambda: str(fake.latitude()),
    'longitude': lambda: str(fake.longitude()),
    'color': lambda: fake.color_name(),
    'currency': lambda: fake.currency(),
    'price': lambda: round(random.uniform(5, 500), 2),
    'number': lambda: random.randint(1, 100),
    'integer': lambda: random.randint(1, 1000),
    'boolean': lambda: random.choice(['True', 'False', 'Yes', 'No']),
    'text': lambda: fake.text(max_nb_chars=50),
    'paragraph': lambda: fake.paragraph(),
    'sentence': lambda: fake.sentence(),
    'precinct': lambda: f"0{random.randint(1000,9999)}E-{random.randint(1,99)}",
    'precinctsplit': lambda: f"0{random.randint(1000,9999)}E-{random.randint(1,99)}_{random.randint(1,9)}",
    'partyname': lambda: fake.last_name(),
    'partyname1': lambda: fake.first_name(),
    'resaddress': lambda: fake.street_address(),
    'mailaddress': lambda: fake.street_address(),
    ' precinctsplitcode': lambda: f"0{random.randint(1000,9999)}E-{random.randint(1,99)}_{random.randint(1,9)}",
    'id': lambda: random.randint(1000, 9999),
    'appcode': lambda: random.choice(['A', 'B', 'C', 'D']),
    'partycode': lambda: random.choice(['REP', 'DEM', 'IND', 'LIB']),
}


@app.route('/generate-fake', methods=['POST'])
def generate_fake():
    try:
        data = request.get_json()
        columns = data.get('columns', [])  # list of column names
        num_rows = int(data.get('numRows', 10))
        output_format = data.get('format', 'csv')
        
        if not columns:
            return jsonify({'error': 'At least one column is required'}), 400
        
        if num_rows < 1 or num_rows > 100000:
            return jsonify({'error': 'Number of rows must be between 1 and 100,000'}), 400
        
        # Build rows
        rows = []
        for _ in range(num_rows):
            row = {}
            for col in columns:
                col_lower = col.lower().strip()
                # Check for matching fake provider
                provider = FAKE_PROVIDERS.get(col_lower)
                if provider:
                    row[col] = provider()
                else:
                    # Default to name for unrecognized columns
                    row[col] = fake.name()
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        if output_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8')
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='fake_data.csv'
            )
        elif output_format == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='FakeData')
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='fake_data.xlsx'
            )
        else:
            return jsonify({'error': 'Unsupported format. Use "csv" or "excel".'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fake-columns', methods=['GET'])
def get_fake_columns():
    """Return list of supported column names for autocomplete"""
    return jsonify({'columns': list(FAKE_PROVIDERS.keys())})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
