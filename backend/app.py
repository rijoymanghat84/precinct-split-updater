from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io
import chardet
from faker import Faker
import random

app = Flask(__name__)
CORS(app)

fake_us = Faker('en_US')
fake_ca = Faker('en_CA')

# Country-aware row generator
def generate_row(columns, allowed_countries=None):
    """Generate a single row with country-aware fields."""
    if allowed_countries is None:
        allowed_countries = ['United States', 'Canada']
    country = random.choice(allowed_countries)
    
    row = {}
    for col in columns:
        col_lower = col.lower().strip()
        
        # Country-aware mappings
        if col_lower == 'country':
            row[col] = country
        elif col_lower in ('zip', 'zipcode'):
            row[col] = fake_us.zipcode() if country == 'United States' else fake_ca.postcode()
        elif col_lower == 'state':
            row[col] = fake_us.state() if country == 'United States' else fake_ca.province()
        elif col_lower == 'city':
            row[col] = fake_us.city() if country == 'United States' else fake_ca.city()
        elif col_lower == 'address':
            row[col] = fake_us.street_address()
        elif col_lower == 'street':
            row[col] = fake_us.street_name()
        elif col_lower == 'phone':
            row[col] = fake_us.phone_number() if country == 'United States' else fake_ca.phone_number()
        elif col_lower == 'currency':
            row[col] = 'USD' if country == 'United States' else 'CAD'
        elif col_lower == 'company':
            row[col] = fake_us.company()
        elif col_lower == 'license':
            row[col] = fake_us.license_plate()
        elif col_lower == 'fname':
            row[col] = fake_us.first_name_male() if random.random() > 0.5 else fake_us.first_name_female()
        elif col_lower == 'firstname':
            row[col] = fake_us.first_name()
        elif col_lower == 'lastname':
            row[col] = fake_us.last_name()
        elif col_lower == 'fullname' or col_lower == 'name':
            row[col] = fake_us.name()
        elif col_lower == 'email':
            row[col] = fake_us.email()
        elif col_lower == 'job':
            row[col] = fake_us.job()
        elif col_lower == 'ssn':
            row[col] = fake_us.ssn() if country == 'United States' else fake_ca.ssn()
        elif col_lower == 'date':
            row[col] = fake_us.date()
        elif col_lower == 'datetime':
            row[col] = fake_us.date_time()
        elif col_lower == 'time':
            row[col] = fake_us.time()
        elif col_lower == 'url':
            row[col] = fake_us.url()
        elif col_lower == 'username':
            row[col] = fake_us.user_name()
        elif col_lower == 'password':
            row[col] = fake_us.password()
        elif col_lower == 'ipv4':
            row[col] = fake_us.ipv4()
        elif col_lower == 'ipv6':
            row[col] = fake_us.ipv6()
        elif col_lower == 'mac':
            row[col] = fake_us.mac_address()
        elif col_lower == 'latitude':
            row[col] = str(fake_us.latitude())
        elif col_lower == 'longitude':
            row[col] = str(fake_us.longitude())
        elif col_lower == 'color':
            row[col] = fake_us.color_name()
        elif col_lower == 'price':
            row[col] = round(random.uniform(5, 500), 2)
        elif col_lower == 'number':
            row[col] = random.randint(1, 100)
        elif col_lower == 'integer':
            row[col] = random.randint(1, 1000)
        elif col_lower == 'boolean':
            row[col] = random.choice(['True', 'False', 'Yes', 'No'])
        elif col_lower == 'text':
            row[col] = fake_us.text(max_nb_chars=50)
        elif col_lower == 'paragraph':
            row[col] = fake_us.paragraph()
        elif col_lower == 'sentence':
            row[col] = fake_us.sentence()
        elif col_lower == 'precinct':
            row[col] = f"0{random.randint(1000,9999)}E-{random.randint(1,99)}"
        elif col_lower in ('precinctsplit', 'precinctsplitcode'):
            row[col] = f"0{random.randint(1000,9999)}E-{random.randint(1,99)}_{random.randint(1,9)}"
        elif col_lower == 'partyname':
            row[col] = fake_us.last_name()
        elif col_lower == 'partyname1':
            row[col] = fake_us.first_name()
        elif col_lower == 'resaddress':
            row[col] = fake_us.street_address()
        elif col_lower == 'mailaddress':
            row[col] = fake_us.street_address()
        elif col_lower == 'id':
            row[col] = random.randint(1000, 9999)
        elif col_lower == 'appcode':
            row[col] = random.choice(['A', 'B', 'C', 'D'])
        elif col_lower == 'partycode':
            row[col] = random.choice(['REP', 'DEM', 'IND', 'LIB'])
        else:
            # Default fallback
            row[col] = fake_us.name()
    
    return row


def detect_encoding(file_bytes, sample_size=10000):
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
        region = data.get('region', 'both')  # 'us' or 'both'
        
        if not columns:
            return jsonify({'error': 'At least one column is required'}), 400
        
        if num_rows < 1 or num_rows > 100000:
            return jsonify({'error': 'Number of rows must be between 1 and 100,000'}), 400
        
        allowed_countries = ['United States'] if region == 'us' else ['United States', 'Canada']
        
        rows = [generate_row(columns, allowed_countries) for _ in range(num_rows)]
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
    return jsonify({'columns': [
        'firstname','lastname','fname','fullname','name','email','phone',
        'address','street','city','state','zip','zipcode','country',
        'company','job','ssn','date','datetime','time','url',
        'username','password','ipv4','ipv6','mac','latitude','longitude',
        'color','currency','price','number','integer','boolean',
        'text','paragraph','sentence','precinct','precinctsplit',
        'partyname','partyname1','resaddress','mailaddress',
        'precinctsplitcode','id','appcode','partycode'
    ]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
