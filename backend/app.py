from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io
import chardet
from faker import Faker
import random

app = Flask(__name__)
CORS(app)

# Use US locale for realistic US/Canada data
fake_us = Faker('en_US')
fake_ca = Faker('en_CA')

def get_fake():
    return random.choice([fake_us, fake_ca])()

FAKE_PROVIDERS = {
    'firstname':   lambda: fake_us.first_name(),
    'lastname':     lambda: fake_us.last_name(),
    'fname':        lambda: fake_us.first_name_male() if random.random() > 0.5 else fake_us.first_name_female(),
    'fullname':     lambda: fake_us.name(),
    'name':         lambda: fake_us.name(),
    'email':        lambda: fake_us.email(),
    'phone':        lambda: fake_us.phone_number(),
    'address':      lambda: fake_us.street_address(),
    'street':       lambda: fake_us.street_name(),
    'city':         lambda: fake_us.city(),
    'state':        lambda: fake_us.state(),
    'zip':          lambda: fake_us.zipcode(),
    'zipcode':      lambda: fake_us.zipcode(),
    'country':      lambda: random.choice(['United States', 'Canada']),
    'company':      lambda: fake_us.company(),
    'job':          lambda: fake_us.job(),
    'ssn':          lambda: fake_us.ssn(),
    'date':         lambda: fake_us.date(),
    'datetime':     lambda: fake_us.date_time(),
    'time':         lambda: fake_us.time(),
    'url':          lambda: fake_us.url(),
    'username':     lambda: fake_us.user_name(),
    'password':     lambda: fake_us.password(),
    'ipv4':         lambda: fake_us.ipv4(),
    'ipv6':         lambda: fake_us.ipv6(),
    'mac':          lambda: fake_us.mac_address(),
    'license':      lambda: fake_us.license_plate(),
    'latitude':     lambda: str(fake_us.latitude()),
    'longitude':    lambda: str(fake_us.longitude()),
    'color':        lambda: fake_us.color_name(),
    'currency':     lambda: random.choice(['USD', 'CAD']),
    'price':        lambda: round(random.uniform(5, 500), 2),
    'number':       lambda: random.randint(1, 100),
    'integer':      lambda: random.randint(1, 1000),
    'boolean':      lambda: random.choice(['True', 'False', 'Yes', 'No']),
    'text':         lambda: fake_us.text(max_nb_chars=50),
    'paragraph':    lambda: fake_us.paragraph(),
    'sentence':     lambda: fake_us.sentence(),
    'precinct':      lambda: f"0{random.randint(1000,9999)}E-{random.randint(1,99)}",
    'precinctsplit': lambda: f"0{random.randint(1000,9999)}E-{random.randint(1,99)}_{random.randint(1,9)}",
    'partyname':     lambda: fake_us.last_name(),
    'partyname1':    lambda: fake_us.first_name(),
    'resaddress':    lambda: fake_us.street_address(),
    'mailaddress':   lambda: fake_us.street_address(),
    'precinctsplitcode': lambda: f"0{random.randint(1000,9999)}E-{random.randint(1,99)}_{random.randint(1,9)}",
    'id':           lambda: random.randint(1000, 9999),
    'appcode':      lambda: random.choice(['A', 'B', 'C', 'D']),
    'partycode':    lambda: random.choice(['REP', 'DEM', 'IND', 'LIB']),
}


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


@app.route('/generate-fake', methods=['POST'])
def generate_fake():
    try:
        data = request.get_json()
        columns = data.get('columns', [])
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
                provider = FAKE_PROVIDERS.get(col_lower)
                if provider:
                    row[col] = provider()
                else:
                    row[col] = fake_us.name()
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
    return jsonify({'columns': list(FAKE_PROVIDERS.keys())})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
