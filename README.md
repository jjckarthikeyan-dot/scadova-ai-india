# Scadova-AI-India: Loan Agency Backend

<div align="center">

**Enterprise Lending & Deterministic Underwriting Backend for Indian Financial Services**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-purple.svg)](https://alembic.sqlalchemy.org)
[![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

</div>

---

## 📌 Project Overview

**Scadova-AI-India** is a multi-tenant backend platform engineered for retail and SME lending in India. The core business module in this repository is the **Loan Agency**, supporting end-to-end loan application lifecycles, deterministic financial calculations (EMI, FOIR, LTV, down payment), Indian credit policy underwriting rule evaluations, and private document processing across:

1. **Business Loans** (MSME, Proprietorship, Partnership, Pvt Ltd)
2. **Personal Loans** (Salaried Professionals)
3. **Used Car Loans** (Asset-backed vehicle financing)

---

## 🏛 Architecture & Folder Structure

The project preserves the exact modular router aggregation architecture of Scadova-AI, isolating domain code in `backend/loan_agency/` while exposing shared infrastructure in `backend/core/` and `backend/common/`.

```
scadova-ai-india/
├── frontend/
│   └── .gitkeep
├── backend/
│   ├── __init__.py
│   ├── main.py                  # Canonical FastAPI application entry point
│   ├── requirements.txt         # Backend Python dependencies
│   ├── core/                    # Infrastructure & shared platform configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic environment settings
│   │   ├── database.py          # SQLAlchemy engine & Supabase client wrapper
│   │   ├── security.py          # JWT, bcrypt hashing & Indian PII data masking
│   │   ├── dependencies.py      # Auth & Role-based access dependencies
│   │   └── tenant.py            # Multi-tenancy context
│   ├── common/                  # Reusable utilities
│   │   ├── __init__.py
│   │   ├── responses.py         # Standardized JSON response envelope
│   │   ├── audit.py             # Redacting audit event logger
│   │   ├── pagination.py        # Pagination models and helpers
│   │   ├── storage.py           # Private signed URL storage abstraction
│   │   └── usage.py             # API usage and quota tracking
│   └── loan_agency/             # Core Loan Agency business module
│       ├── __init__.py
│       ├── router.py            # Parent aggregator router for /api/loan-agency
│       ├── applications.py      # Application lifecycle CRUD & status workflows
│       ├── business_loans.py    # Business loan data capture & retrieval
│       ├── personal_loans.py    # Personal salaried loan data capture & retrieval
│       ├── used_car_loans.py    # Used car loan data capture & retrieval
│       ├── documents.py         # Presigned upload URLs & document management
│       ├── analysis.py          # Underwriting analysis & rule assessment
│       ├── calculations.py      # Deterministic Decimal financial calculations
│       ├── rules.py             # Indian credit underwriting rule engine
│       ├── models.py            # SQLAlchemy database models
│       ├── schemas.py           # Pydantic schemas & validations
│       ├── repository.py        # Database CRUD persistence layer
│       └── service.py           # Underwriting & calculation coordinator
├── tests/                       # Complete automated test suite
│   ├── conftest.py              # Test client fixtures & in-memory SQLite DB
│   ├── test_health.py           # Root, health & readiness tests
│   ├── test_applications.py     # End-to-end application lifecycle tests
│   ├── test_calculations.py     # Decimal financial precision tests
│   ├── test_rules.py            # PASS, REFER, DECLINE, DATA_REQUIRED tests
│   └── test_security.py         # Masking & JWT token tests
├── docs/
│   ├── API.md                   # Detailed REST API endpoint specification
│   └── DATABASE.md              # Database schema & entity relationships
├── alembic/                     # Database migrations
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
├── alembic.ini                  # Alembic migration configuration
├── requirements.txt             # Root requirements
├── .env.example                 # Example environment variables
├── .gitignore
├── Dockerfile                   # Production container definition
├── docker-compose.yml           # Multi-container orchestration with PostgreSQL
├── main.py                      # Root backward-compatibility entry point
└── README.md
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- `pip` or virtualenv
- PostgreSQL (or local SQLite for development)

### 2. Setup Virtual Environment & Dependencies

```bash
# Clone or navigate to the repository
cd /path/to/scadova-ai-india

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```ini
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0
JWT_SECRET_KEY=your-super-secret-key-at-least-32-chars
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
STORAGE_BUCKET=loan-agency-documents
```

*(Note: The API runs seamlessly in local/mock mode even without active Supabase credentials).*

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the FastAPI Development Server

```bash
uvicorn backend.main:app --reload
```

The API will be available at:
- **Interactive OpenAPI UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Root Info**: [http://localhost:8000/](http://localhost:8000/)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running the Test Suite

Run the full pytest suite:

```bash
pytest -v
```

All 19 tests will validate:
- Root, health, and liveness endpoints
- Application CRUD and workflow transitions
- Business, Personal, and Used Car loan profiles
- Decimal-accurate EMI, FOIR, and LTV calculations
- Underwriting rule outcomes (`PASS`, `REFER`, `DECLINE`, `DATA_REQUIRED`)
- PAN, Aadhaar, Account, and Mobile masking
- Document presigned uploads and completions

---

## 🔒 Security & Data Masking

Scadova-AI-India strictly protects sensitive Indian financial PII:
- **PAN**: Masked as `AB******4F`
- **Aadhaar**: Never stored raw; masked as `********1098`
- **Bank Account Number**: Masked as `********9012`
- **Mobile Number**: Masked as `******3210`
- **Logs**: All payload dumps automatically redact passwords, secrets, tokens, and PII via `redact_sensitive_payload()`.
- **Documents**: Uploaded to private buckets with temporary signed URLs (5–15 min expiry).

---

## 🐳 Docker Deployment

To launch the backend with PostgreSQL in Docker:

```bash
docker-compose up --build -d
```