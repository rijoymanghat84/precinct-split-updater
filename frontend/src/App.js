import React, { useState } from 'react';
import Papa from 'papaparse';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('process');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  // Fake data generator state
  const [colInput, setColInput] = useState('');
  const [numRows, setNumRows] = useState(100);
  const [outputFmt, setOutputFmt] = useState('csv');
  const [generating, setGenerating] = useState(false);
  const [fakeMessage, setFakeMessage] = useState(null);
  const [availableColumns] = useState([
    'firstname','lastname','email','phone','address','city','state','zip','country',
    'company','job','ssn','date','datetime','url','username','password','number',
    'integer','boolean','text','paragraph','sentence','precinct','precinctsplit',
    'partyname','partyname1','resaddress','mailaddress','id','appcode','partycode',
    'fullname','name','street','color','currency','price','latitude','longitude',
    'license','ssn','ipv4','ipv6','mac'
  ]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setMessage(null);
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
        setMessage({ type: 'success', text: 'CSV processed! Download started.' });
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.error || 'Processing failed' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Error uploading file. Make sure the backend is running.' });
    }
    setUploading(false);
  };

  const handleGenerate = async () => {
    if (!colInput.trim()) {
      setFakeMessage({ type: 'error', text: 'Please enter at least one column name' });
      return;
    }
    setGenerating(true);
    setFakeMessage(null);
    try {
      const response = await fetch('/generate-fake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          columns: colInput.split(',').map(c => c.trim()).filter(c => c),
          numRows: parseInt(numRows),
          format: outputFmt
        })
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fake_data.${outputFmt}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        setFakeMessage({ type: 'success', text: `Generated ${numRows} rows! Download started.` });
      } else {
        const error = await response.json();
        setFakeMessage({ type: 'error', text: error.error || 'Generation failed' });
      }
    } catch (err) {
      setFakeMessage({ type: 'error', text: 'Error generating data. Make sure backend is running.' });
    }
    setGenerating(false);
  };

  return (
    <div className="container">
      <header className="header">
        <h1>📋 Precinct Split Updater</h1>
        <p>Tools for CSV processing & fake data generation</p>
      </header>

      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'process' ? 'active' : ''}`}
          onClick={() => setActiveTab('process')}
        >
          🔢 CSV Processor
        </button>
        <button
          className={`tab-btn ${activeTab === 'generate' ? 'active' : ''}`}
          onClick={() => setActiveTab('generate')}
        >
          🎭 Fake Data Generator
        </button>
      </div>

      <main className="main">
        {/* ====== TAB 1: CSV PROCESSOR ====== */}
        {activeTab === 'process' && (
          <div className="tab-content">
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
              <div className={`message ${message.type}`}>{message.text}</div>
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
                        <th className="new-col">Start Page</th>
                        <th className="new-col">End Page</th>
                      </tr>
                    </thead>
                    <tbody>
                      {preview.data.map((row, i) => (
                        <tr key={i}>
                          {preview.meta.fields.map(field => (
                            <td key={field}>{row[field]}</td>
                          ))}
                          <td className="new-col muted">(generated)</td>
                          <td className="new-col muted">(generated)</td>
                          <td className="new-col muted">(generated)</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ====== TAB 2: FAKE DATA GENERATOR ====== */}
        {activeTab === 'generate' && (
          <div className="tab-content">
            <div className="fake-panel">
              <div className="form-row">
                <label className="form-label">
                  📄 Output Format
                </label>
                <select
                  className="form-select"
                  value={outputFmt}
                  onChange={e => setOutputFmt(e.target.value)}
                >
                  <option value="csv">CSV (.csv)</option>
                  <option value="excel">Excel (.xlsx)</option>
                </select>
              </div>

              <div className="form-row">
                <label className="form-label">
                  📋 Column Names
                  <span className="label-hint">(comma-separated)</span>
                </label>
                <textarea
                  className="form-textarea"
                  placeholder="e.g. firstname, lastname, email, address, city, state, zip"
                  value={colInput}
                  onChange={e => setColInput(e.target.value)}
                  rows={3}
                />
                <div className="col-chips">
                  {availableColumns.map(col => (
                    <button
                      key={col}
                      className="col-chip"
                      onClick={() => {
                        if (colInput) {
                          setColInput(prev => prev + ', ' + col);
                        } else {
                          setColInput(col);
                        }
                      }}
                    >
                      + {col}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-row">
                <label className="form-label">
                  🔢 Number of Records
                </label>
                <input
                  type="number"
                  className="form-input"
                  value={numRows}
                  onChange={e => setNumRows(e.target.value)}
                  min={1}
                  max={100000}
                />
                <div className="quick-numbers">
                  {[10, 100, 500, 1000, 5000].map(n => (
                    <button key={n} className="quick-num-btn" onClick={() => setNumRows(n)}>
                      {n}
                    </button>
                  ))}
                </div>
              </div>

              {fakeMessage && (
                <div className={`message ${fakeMessage.type}`}>{fakeMessage.text}</div>
              )}

              <button
                className="process-btn generate-btn"
                onClick={handleGenerate}
                disabled={generating}
              >
                {generating ? '⏳ Generating...' : `🎲 Generate ${numRows} Fake Records`}
              </button>

              <div className="fake-note">
                <p>💡 <strong>Tip:</strong> Click column chips to add them quickly. Column names are case-insensitive.</p>
                <p>Supported: names, emails, addresses, phone numbers, dates, precinct codes, and more.</p>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>🔢 CSV Processor: Groups by Precinct Split → adds sequence codes & page numbers | 🎭 Fake Generator: Create test data instantly</p>
      </footer>
    </div>
  );
}

export default App;
