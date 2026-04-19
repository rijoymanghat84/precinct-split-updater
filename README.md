# Precinct Split Updater - Web App

A lightweight web app that processes CSV files containing a `Precinct Split` column. It groups rows by precinct split code and adds a new column `Updated Precinct Split Code` with zero-padded sequence numbers.

## Features

- 📁 Drag & drop CSV upload
- 👁️ Live preview of your data
- 🔢 Automatic sequence numbering per group
- ⬇️ Download processed CSV instantly

## Tech Stack

- **Frontend:** React + Papaparse
- **Backend:** Flask + Pandas
- **Docker:** Docker Compose for easy deployment

## Quick Start (Docker)

```bash
# Build and run
docker-compose up --build

# Open in browser
open http://localhost:3000
```

## Manual Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## How It Works

| Row | Precinct Split | Updated Precinct Split Code |
|-----|----------------|------------------------------|
| 1 | `01000e1_1` | `01000e1_1_001` |
| 2 | `01000e1_1` | `01000e1_1_002` |
| 3 | `01000e1_1` | `01000e1_1_003` |

Each unique precinct split code gets its own sequence starting from `_001`.

## Project Structure

```
precinct-split-updater/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
└── Dockerfile.frontend
```
