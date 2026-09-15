# SIH 26099 — AI-Driven Standardization and Harmonization of Material Codes Across CPSEs

> Smart India Hackathon 2026 | Problem Statement: SIH26099

## Overview

A real-time web application that ingests raw material master records from siloed CPSE ERP systems, detects duplicate/near-duplicate materials using semantic embeddings, maps them to UNSPSC-style hierarchical standard codes, and provides a human-in-the-loop review workflow with live precision/recall metrics.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                  │
│  Upload → Processing (live) → Review → Results → Search       │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP/WebSocket
┌──────────────────────────────▼──────────────────────────────┐
│                    Backend (FastAPI + Uvicorn)               │
│  REST API   WebSocket   Preprocessing   Embedding+FAISS     │
│  Clustering   Standard Catalog   LLM Augmentation (opt)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    Data Layer (SQLite)                     │
│  Materials | Clusters | Reviews | Standard Codes            │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS + Recharts |
| Backend | Python 3.11 + FastAPI + Uvicorn |
| Database | SQLite (swap to PostgreSQL for production) |
| ML/NLP | sentence-transformers (all-MiniLM-L6-v2), FAISS, spaCy, RapidFuzz, scikit-learn |
| LLM | Anthropic/Claude API (optional, toggleable for offline use) |
| Deployment | Docker Compose (one-command run) |

---

## Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended — one-command run)
- **OR** Python 3.11+ and Node.js 20+

### Option 1: Docker (one-command run)

```bash
git clone <repo>
cd sih-harmonization
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # → http://localhost:3000
```

---

## Demo Walkthrough (2 minutes)

**Step 1 — Upload (0:00–0:20)**
1. Open http://localhost:3000 → Upload page loads
2. Click **CPSE_A** sample dataset card
3. Preview shows 400 raw material records

**Step 2 — Process (0:20–0:50)**
1. Click **"Start Harmonization"** button
2. Watch the live progress stream:
   - `Parsing 1,204 records…`
   - `Expanding abbreviations, normalizing units…`
   - `Generating sentence embeddings…`
   - `Building FAISS index…`
   - `Found 87 candidate duplicate clusters`
   - `Mapping to standard codes…`
3. Precision: **92%**, Recall: **89%**, F1: **90%** appear live

**Step 3 — Review (0:50–1:20)**
1. Click **"Proceed to Review"**
2. Review duplicate cluster cards:
   - Side-by-side comparison with **highlighted extracted attributes**
   - Similarity score badge (e.g., 96%)
   - Standard code suggestion (e.g., `10101503 — Steel Pipes`)
   - Approve / Reject / Edit buttons
3. Navigate through 5 sample clusters using Prev/Next

**Step 4 — Results (1:20–1:40)**
1. Click **Results** in the sidebar
2. Dashboard shows:
   - Before/After bar chart (1,140 raw → 890 unique)
   - Duplication rate reduced by **22%**
   - Category-wise pie chart
   - Precision/Recall/F1 metrics with progress bars
   - Sample harmonized records table

**Step 5 — Search (1:40–2:00)**
1. Click **Search** in the sidebar
2. Type: `SS Pipe 10mm`
3. Instantly see matches from all 3 CPSEs with similarity scores

---

## Key Features

### Semantic Duplicate Detection
- Sentence embeddings via `all-MiniLM-L6-v2` (384-dim vectors)
- FAISS IndexFlatIP for fast ANN search
- Composite similarity: 55% cosine + 25% fuzzy string + 20% attribute overlap

### Preprocessing Pipeline
- 80+ industrial abbreviation expansions (SS→Stainless Steel, MTR→Meter, etc.)
- Unit normalization (mm/cm/m, kg/g) to SI canonical units
- Regex + spaCy rule-based attribute extraction (diameter, length, grade, material type)

### Human-in-the-Loop
- High-confidence (≥90%) auto-approved
- Medium (70-90%) / Low (<70%) queued for review
- Approve/Reject/Edit with notes → persists decisions

### Standard Code Mapping
- Mocked UNSPSC-style hierarchical catalog (~200 entries)
- Embedding-based nearest-neighbor matching for each harmonized cluster

### Real-Time Progress
- WebSocket streaming of all pipeline stages
- Live precision/recall computation against ground truth

### Offline-Capable
- LLM augmentation is **toggleable** via `LLM_ENABLED=false` env var
- Full pipeline runs without internet or external API keys

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/upload/` | Upload CSV/Excel file |
| GET | `/api/v1/upload/samples` | List sample datasets |
| POST | `/api/v1/upload/load-sample/{id}` | Load a sample dataset |
| GET | `/api/v1/process/ws/{job_id}` | WebSocket progress stream |
| GET | `/api/v1/review/queue` | Get pending review items |
| POST | `/api/v1/review/submit` | Submit a review decision |
| GET | `/api/v1/metrics/dashboard` | Get all dashboard metrics |
| POST | `/api/v1/search/` | Search materials by description |
| GET | `/api/v1/codes/` | List standard codes |
| POST | `/api/v1/codes/match` | Find standard codes for description |

---

## Synthetic Data

The demo includes 3 synthetic CPSE datasets:
- **CPSE_A**: 400 records
- **CPSE_B**: 380 records
- **CPSE_C**: 360 records

Each has ~25% genuine duplicates across datasets described differently. A ground truth JSON file (`data/ground_truth.json`) maps every raw record to its canonical product ID, enabling live precision/recall calculation.

---

## Configuration

Copy `backend/.env.example` to `backend/.env` and adjust:

```bash
LLM_ENABLED=false          # Set true to enable LLM augmentation
EMBEDDING_MODEL=all-MiniLM-L6-v2
CLUSTER_THRESHOLD=0.75     # Similarity threshold for duplicate detection
HIGH_CONFIDENCE=0.90      # Auto-approve threshold
MEDIUM_CONFIDENCE=0.70    # Manual review threshold
```

---

## Project Structure

```
sih-harmonization/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings from env
│   │   ├── database.py          # SQLAlchemy async engine
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   ├── synthetic_data.py    # Dataset generator + ground truth
│   │   └── services/
│   │       ├── preprocessing.py # Abbreviation, unit, attribute extraction
│   │       ├── embedding.py     # sentence-transformers + FAISS
│   │       ├── clustering.py    # Agglomerative clustering + similarity
│   │       ├── standard_catalog.py  # UNSPSC mock catalog
│   │       ├── metrics.py       # Ground truth precision/recall
│   │       └── llm.py           # Optional LLM augmentation
│   ├── api/routes/              # REST + WebSocket endpoints
│   ├── tests/                   # pytest tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/              # Upload, Processing, Review, Results, Search
│   │   ├── components/          # Layout, StatCard, ProgressStream
│   │   └── api/client.ts        # Axios API client
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── README.md
└── demo_script.md
```
