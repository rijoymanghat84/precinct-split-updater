from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import io
import chardet

app = Flask(__name__)
CORS(app)


def detect_encoding(file_bytes, sample_size=10000):
    """Detect file encoding, fallback to latin-1 which handles most bytes"""
    result = chardet.detect(file_bytes[:sample_size])
    detected = result['encoding'] or 'utf-8'
    # Force common non-utf8 encodings that chardet might misdetect
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
        
        # Detect encoding
        encoding = detect_encoding(file_bytes)
        
        # Read CSV with detected encoding
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
        
        # Check if Precinct Split column exists
        if 'Precinct Split' not in df.columns:
            return jsonify({'error': 'CSV must have a "Precinct Split" column'}), 400
        
        # Group by Precinct Split and add sequence numbers
        def add_sequence(group):
            group = group.copy()
            # Create Updated Precinct Split Code: original + _zero-padded sequence
            group['Updated Precinct Split Code'] = [
                f"{code}_{str(i).zfill(3)}" for code, i in zip(group['Precinct Split'], range(1, len(group) + 1))
            ]
            return group
        
        # Apply to each group
        df = df.groupby('Precinct Split', group_keys=False).apply(add_sequence)
        
        # Sort back to original order (optional but nice)
        df = df.sort_index().reset_index(drop=True)
        
        # Generate CSV output (always use utf-8 for output)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
