# Smart Resume Screening System

Lightweight resume screening app using FastAPI (backend) and Streamlit (frontend). It extracts skills and experience from PDF resumes and scores matches against a job description using TF-IDF + keyword matching.

**Project Structure**

```
README.md
backend/
  ├─ main.py            # FastAPI app (ASGI entrypoint)
  ├─ resume_parser.py   # PDF parsing + skill/experience extraction
  ├─ matcher.py         # TF-IDF, skill matching, experience scoring
  └─ requirements.txt   # Backend dependencies (pinned)
frontend/
  └─ streamlit_app.py   # Streamlit UI

```

## Prerequisites

- Python 3.10+ (3.14 tested here)
- Git (optional)

This repository uses virtual environments to avoid dependency conflicts between the backend (FastAPI) and the frontend (Streamlit). Streamlit pulls a different compatible version of `starlette`, so the frontend runs in a separate venv.

## Setup (Windows PowerShell)

1. Clone repo and change directory:

```powershell
git clone <repo-url> resume-screening-system
cd resume-screening-system
```

2. Create and activate the project (backend) virtualenv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install backend dependencies:

```powershell
pip install -r backend/requirements.txt
```

Notes:
- `backend/requirements.txt` includes a pin for `starlette==0.27.0` to keep FastAPI compatible with the Router signature used by this code.
- If `spaCy` model is not present, download it with:

```powershell
.venv\Scripts\python.exe -m spacy download en_core_web_sm
```

4. (Optional but recommended) Create an isolated venv for the Streamlit frontend to avoid `starlette` version conflicts:

```powershell
python -m venv frontend/.venv
frontend/.venv\Scripts\Activate.ps1
pip install streamlit requests
```

The repository already created a frontend venv at `frontend/.venv` when the app was started locally.

## Running the App

Open two separate terminals (or tabs): one for backend, one for frontend.

Backend (in project venv):

```powershell
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000 --host 127.0.0.1
```

Health check (backend):

```powershell
curl http://127.0.0.1:8000/health
# expected JSON: {"status":"healthy","message":"API is running"}
```

Frontend (in frontend venv):

```powershell
frontend/.venv\Scripts\python.exe -m streamlit run frontend/streamlit_app.py --server.port 8501
```

Open the UI at: http://localhost:8501

## How the System Works (Approach)

- `backend/resume_parser.py`:
  - Uses `PyPDF2` to extract text from uploaded PDF resumes.
  - Uses a small spaCy model (`en_core_web_sm`) to support NLP; the current parser primarily uses keyword matching from an internal `skills_list`.
  - Extracts `skills` (keyword matching) and `experience` (regex patterns for years).

- `backend/matcher.py`:
  - Uses `sklearn`'s `TfidfVectorizer` to compute TF-IDF vectors for resume text vs job description and measures cosine similarity (TF-IDF similarity).
  - Extracts required skills from the JD and computes a skill-match percentage by comparing the JD skill set to resume-extracted skills.
  - Computes an experience match score by parsing a required years value from the JD and comparing it to the resume's years (exponential decay if under requirement).
  - Combines scores using weights: Skills 50%, TF-IDF 30%, Experience 20% to produce a final `match_score` (0-100).
  - Returns `matched_skills`, `missing_skills`, `detailed_scores`, and a human-readable `explanation`.

- `frontend/streamlit_app.py`:
  - Uploads a PDF and job description to the backend `/match` endpoint and displays metrics, matched/missing skills, and recommendations.

## API Endpoints

- `GET /health` – health check
- `POST /match` – multipart form-data:
  - `resume_file` (PDF file)
  - `job_description` (text)

Response includes `match_score`, `matched_skills`, `missing_skills`, `detailed_scores`, and `resume_metadata`.

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'resume_parser'`, make sure you run uvicorn with the module path `backend.main:app` (not `main:app`) from the repository root.
- If spaCy errors occur, ensure `en_core_web_sm` is downloaded into the same env used to run the backend.
- If Streamlit fails to start with starlette-related import errors, run the frontend from its own venv (`frontend/.venv`) as described above.

## Notes & Next Steps

- I pinned `starlette==0.27.0` in `backend/requirements.txt` to avoid incompatibilities with the installed FastAPI version. Keep an eye on dependency updates.
- If you want, I can:
  - Add a `Makefile` or `scripts/` helpers for Windows to simplify run commands.
  - Add a small test fixture or sample resume PDF + sample JD for quick demoing.

---

Developed and validated locally — FastAPI backend at `http://127.0.0.1:8000` and Streamlit frontend at `http://localhost:8501`.
# Smart Resume Screening System

A complete resume screening solution with FastAPI backend and Streamlit frontend.

## Features
- 📄 Upload PDF resumes
- 🎯 AI-powered matching (TF-IDF + skill-based)
- 📊 Detailed match scores and analysis
- 💡 Easy-to-use web interface
- 🚀 REST API for integration

## Architecture
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Streamlit │────▶│ FastAPI │────▶│ Resume │
│ Frontend │ │ Backend │ │ Matcher │
└─────────────┘ └─────────────┘ └─────────────┘