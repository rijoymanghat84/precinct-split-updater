# BelWo Data Utilities

A lightweight web app for CSV processing and test data generation. Built with React + Flask and Docker.

## Features

### 🔢 CSV Processor
Upload a CSV with a **Precinct Split** column. The tool automatically adds:
- `Updated Precinct Split Code` — zero-padded sequence per group (_001, _002, ...)
- `Start Page` — continuous page numbering (every record = 2 pages)
- `End Page` — end page for each record

### 🎭 Test Data Generator
Generate realistic fake test data with full control:
- Choose **CSV** or **Excel** output
- Define custom **column names** (case-insensitive)
- Generate **1 to 100,000 records** instantly
- Clickable column chips for quick selection

## Quick Start (Docker)

```bash
git clone https://github.com/rijoymanghat84/precinct-split-updater.git
cd precinct-split-updater
docker-compose up --build
```

Open **http://localhost:3000**

## Project Structure

```
precinct-split-updater/
├── backend/
│   ├── app.py              # Flask API (CSV processing + fake data)
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js          # React app
│   │   └── App.css         # BelWo-styled CSS
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
└── Dockerfile.frontend
```

## Environment

- **Frontend:** React (port 3000)
- **Backend:** Flask API (port 5000)
- **Proxy:** Frontend proxies `/process` and `/generate-fake` to Flask

## BelWo

Enterprise document solutions — Output Management, Document Automation, CCM.
