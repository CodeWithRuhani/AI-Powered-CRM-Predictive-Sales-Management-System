# Claude2 — AI-Powered CRM & Predictive Sales Management

A Python proof of concept for Assignment 02. It includes CRM lead CRUD, sales representative assignment, interaction history, a trained Scikit-learn conversion classifier, lead categories, follow-up recommendations, overdue follow-ups, sales analytics and an Ollama-powered chat assistant.

**UI:** intentionally minimal chat interface, matching the supplied reference. Users can provide an email or continue as a guest. **Frontend:** plain HTML/CSS/JavaScript served by FastAPI. **Backend:** FastAPI + SQLAlchemy + SQLite. **AI:** Ollama for chat and natural-language follow-up; Random Forest for lead conversion prediction.

> ML training data is synthetic and reproducible. Its probability is a demo estimate, not a validated business forecast. Ollama is an external local service; install and start it separately. CRM APIs still start if Ollama is unavailable.

## 1. Assignment requirements covered

- Lead create, list, search, filter, detail, update, delete.
- Lead fields: name, company, email, phone, industry, interested service, source, budget, status, assigned sales rep.
- Statuses: New, Contacted, Interested, Negotiation, Converted, Lost.
- ML score 0–100, conversion probability, Hot/Warm/Cold category and explanation.
- Interaction logging: Call, Email, Meeting, Enquiry, Note.
- Individual lead interaction, prediction and follow-up history.
- Ollama follow-up recommendation and suggested message; deterministic fallback if Ollama is down.
- Pending overdue follow-up list.
- Analytics: total/new/converted/lost leads, conversion rate, category counts, representative performance and a 30-day new-lead trend.
- ML evaluation: accuracy, precision, recall, F1 and ROC-AUC.
- Swagger API documentation.

## 2. Folder structure

```text
claude2/
├── app/
│   ├── config.py          # Environment configuration
│   ├── database.py        # SQLAlchemy engine/session
│   ├── models.py          # Relational ORM entities
│   ├── schemas.py         # Pydantic validation
│   ├── repositories.py    # Data access + CRM manager
│   ├── ml_model.py        # Dataset, training, evaluation, prediction
│   ├── ollama.py          # Ollama chat/generation client
│   ├── services.py        # Follow-up recommendation service
│   ├── routes.py          # REST API endpoints
│   └── main.py            # FastAPI entry point
├── frontend/index.html    # Minimal chat + optional email/guest entry
├── data/                  # Synthetic sample and data notes
├── models/                # Saved model created at first start
├── tests/test_api.py
├── schema.sql
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example           # Safe local configuration defaults
├── DEMO_QUESTIONS.md
└── README.md
```

## 3. Prerequisites

- Windows 10/11, macOS or Linux.
- Python 3.10+ (Python 3.11 recommended).
- Ollama installed from https://ollama.com/download.
- Default Ollama model: `llama3.2:3b`.
- Docker Desktop only if using Docker.

## 4. Windows setup (PowerShell)

Open PowerShell in the extracted `claude2` directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

The default `.env` values are configured for Ollama running on the same Windows machine.

## 5. Ollama setup

Install and open Ollama. In a separate PowerShell terminal:

```powershell
ollama pull llama3.2:3b
ollama list
Invoke-RestMethod http://localhost:11434/api/tags
```

If you use a different already-downloaded model, update `OLLAMA_MODEL` in `.env` and restart FastAPI. Local model responses can take several minutes, especially on the first request; `OLLAMA_TIMEOUT` defaults to 300 seconds and `OLLAMA_CONNECT_TIMEOUT` defaults to 5 seconds. Adjust these in `.env` if needed and restart FastAPI for changes to take effect. If Ollama is on another machine, set `OLLAMA_BASE_URL` to its reachable address.

## 6. Start the application

From the project root, with the virtual environment activated:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:
- Chat UI: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

**No separate frontend server is required.** FastAPI serves `frontend/index.html` and the browser calls the same-origin API, avoiding CORS setup. On first start the app trains and saves the model to `models/lead_conversion.joblib` and creates `data/crm.db`.

## 7. Docker

Copy `.env.example` to `.env`. When Ollama runs on the Windows host and the CRM runs in Docker, set this in `.env`:

```dotenv
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Then:

```powershell
docker compose up --build
```

Open http://localhost:8000/. Stop:

```powershell
docker compose down
```

Database and trained model directories are mounted as volumes. If Ollama is unavailable, the API still starts; chat reports the connection issue and follow-up generation uses a local deterministic fallback.

## 8. REST API reference

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/leads` | Create a lead |
| GET | `/leads` | List; optional `search`, `status`, `industry` filters |
| GET | `/leads/{id}` | Lead details |
| PUT | `/leads/{id}` | Update a lead |
| DELETE | `/leads/{id}` | Delete a lead and linked history |
| POST | `/leads/{id}/score` | Persist a new ML prediction |
| GET | `/leads/{id}/history` | Interactions, predictions and follow-ups |
| GET/POST | `/representatives` | List/create sales reps |
| POST | `/interactions` | Record a sales interaction |
| POST | `/followups/recommend?lead_id=1` | Generate and store recommendation |
| GET | `/followups/overdue` | Pending follow-ups past due |
| GET | `/analytics` | Sales KPIs and representative performance |
| GET | `/ml/metrics` | Synthetic holdout evaluation metrics |
| POST | `/chat` | Ollama assistant chat |
| GET | `/health` | API and Ollama configuration status |

### Example PowerShell API flow

Create representative:

```powershell
$rep = Invoke-RestMethod -Method Post http://127.0.0.1:8000/representatives -ContentType "application/json" -Body '{"name":"Riya Mehta","email":"riya@example.com","role":"Sales Executive"}'
```

Create lead:

```powershell
$body = @{name="Aarav Sharma";company="Northstar Technologies";email="aarav@example.com";phone="+91-9876543210";industry="Technology";interested_service="AI Automation";lead_source="Referral";budget=85000;assigned_to=$rep.id} | ConvertTo-Json
$lead = Invoke-RestMethod -Method Post http://127.0.0.1:8000/leads -ContentType "application/json" -Body $body
```

Add interaction, score and recommend:

```powershell
$interaction = @{lead_id=$lead.id;interaction_type="Meeting";interaction_notes="Discussed requirements; requested a product demo."} | ConvertTo-Json
Invoke-RestMethod -Method Post http://127.0.0.1:8000/interactions -ContentType "application/json" -Body $interaction
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/leads/$($lead.id)/score"
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/followups/recommend?lead_id=$($lead.id)"
Invoke-RestMethod "http://127.0.0.1:8000/leads/$($lead.id)/history"
Invoke-RestMethod http://127.0.0.1:8000/analytics
```

## 9. ML implementation

- **Algorithm:** RandomForestClassifier inside a Scikit-learn Pipeline.
- **Features:** industry, lead source, budget, interaction count, days since last contact, service interest.
- **Preprocessing:** OneHotEncoder for categorical features; StandardScaler for numeric features.
- **Data:** 1,200 synthetic examples generated locally using a fixed random seed and a documented probability formula with noise.
- **Split:** stratified 75% training / 25% test.
- **Metrics:** accuracy, precision, recall, F1 and ROC-AUC.
- **Probability:** `predict_proba()`; score = probability × 100. Hot ≥70, Warm ≥40, Cold <40.
- **Persistence:** Joblib model saved under `models/`.

Synthetic outcomes are generated from known signals. High metrics on this artificial dataset do not establish real-world performance. A production model needs representative historical outcomes, time-based validation, leakage checks, calibration and drift monitoring.

## 10. Ollama integration

- Chat: Ollama `/api/chat` endpoint.
- Follow-up text: Ollama `/api/generate` endpoint with lead details and recent interaction notes.
- Default model is configurable with `OLLAMA_MODEL`.
- The chat assistant is conversational; CRM database mutations are exposed as explicit APIs and are not guessed from free-form chat messages.
- If Ollama is offline, chat returns a clear error message; follow-up recommendation uses a deterministic local fallback.

## 11. Database relationships and OOP

- A sales representative can own many leads.
- A lead has many interactions, predictions and follow-ups.
- Deleting a lead cascades to its dependent activity and prediction records.
- Deleting a representative sets lead assignment to NULL.
- `LeadScoringModel`, `FollowUpRecommender`, `OllamaClient`, `LeadRepository` and `CRMManager` separate ML, integration, data access and business coordination.
- SQLAlchemy entity classes represent the relational data model.

## 12. Tests and troubleshooting

Run tests:

```powershell
pytest -q
```

Common fixes:
1. `ollama` not recognised: install Ollama and reopen terminal.
2. Model missing: `ollama pull llama3.2:3b`.
3. Connection refused: start Ollama and test `/api/tags`.
4. Port in use: use `--port 8001`, then visit `http://127.0.0.1:8001/`.
5. PowerShell blocks activation: use the process-scoped execution policy command above.
6. Docker cannot access Ollama: use `host.docker.internal` in `.env`.

## 13. Demo questions

See `DEMO_QUESTIONS.md` for easy, medium and hard interview questions and a suggested walkthrough. Chat questions are answered by Ollama. For live CRM operations use Swagger UI.

## 14. Submission checklist

- Run the application locally and capture screenshots of profile gate, chat, Swagger lead creation, prediction, history and analytics.
- Explain the synthetic-data limitation accurately.
- No real email or WhatsApp sending is implemented; the assignment does not require those integrations.
- Never commit `.env`, real customer data or credentials.
