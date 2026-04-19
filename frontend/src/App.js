import React, { useState } from 'react';
import Papa from 'papaparse';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setMessage(null);
      
      // Preview first few rows
      Papa.parse(selectedFile, {
        preview: 5,
        header: true,
        complete: (results) => {
          setPreview(results);
        }
      });
    } else {
      setMessage({ type: 'error', text: 'Please select a valid CSV file' });
      setFile(null);
      setPreview(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/process', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'updated_precinct_split.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        setMessage({ type: 'success', text: 'CSV processed successfully! Download started.' });
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.error || 'Processing failed' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Error uploading file. Make sure the backend is running.' });
    }

    setUploading(false);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>📋 Precinct Split Updater</h1>
        <p>Upload your CSV file to add Updated Precinct Split Codes</p>
      </header>

      <main className="main">
        <div className="upload-section">
          <div className="file-input-wrapper">
            <input 
              type="file" 
              accept=".csv" 
              onChange={handleFileChange}
              id="file-input"
              className="file-input"
            />
            <label htmlFor="file-input" className="file-label">
              <span className="upload-icon">📁</span>
              <span>{file ? file.name : 'Choose CSV File'}</span>
            </label>
          </div>

          {file && (
            <button 
              className="process-btn" 
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? '⏳ Processing...' : '🚀 Process CSV'}
            </button>
          )}
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        {preview && (
          <div className="preview-section">
            <h2>📊 Preview (first 5 rows)</h2>
            <div className="table-wrapper">
              <table className="preview-table">
                <thead>
                  <tr>
                    {preview.meta.fields.map(field => (
                      <th key={field}>{field}</th>
                    ))}
                    <th className="new-col">Updated Precinct Split Code</th>
                  </tr>
                </thead>
                <tbody>
                  {preview.data.map((row, i) => (
                    <tr key={i}>
                      {preview.meta.fields.map(field => (
                        <td key={field}>{row[field]}</td>
                      ))}
                      <td className="new-col muted">
                        (generated after processing)
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>How it works: Groups by Precinct Split → adds _001, _002, _003... to each row</p>
      </footer>
    </div>
  );
}

export default App;
