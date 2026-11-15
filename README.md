# Scadova AI India — Lending Backend

**Python · FastAPI · SQLAlchemy · Financial Workflows**

An application backend structured around loan intake, underwriting calculations, and document workflows for Indian retail and small-business lending use cases.

## Overview

The documented Loan Agency domain covers:

- Business loan applications
- Personal loan applications
- Used-car loan applications
- Application lifecycle and status transitions
- Financial calculations such as EMI, FOIR, LTV, and down payment
- Rule-based underwriting assessment
- Document upload and management interfaces

**Status:** Repository documentation describes the architecture and intended workflows. This README does not claim production deployment, regulatory certification, or verified test results.

## Architecture

\`\`\`text
FastAPI application
  ├─ Core configuration and security
  ├─ Authentication and tenancy context
  ├─ Loan Agency API routes
  │   ├─ Applications and product-specific intake
  │   ├─ Calculations and underwriting rules
  │   └─ Documents
  └─ Persistence and shared utilities
       ├─ SQLAlchemy models
       ├─ Database access
       └─ Audit / response helpers
\`\`\`

## Key directories

| Path | Responsibility |
| --- | --- |
| \`backend/main.py\` | FastAPI application entry point |
| \`backend/core/\` | Configuration, database, security, tenant context |
| \`backend/loan_agency/\` | Loan domain routes, rules, models, services |
| \`backend/common/\` | Shared API, audit, storage, and usage helpers |
| \`alembic/\` | Database migration definitions |
| \`tests/\` | Test suite |
| \`docs/\` | API and data documentation |

## Local development

Requires Python 3.10+ and a compatible database setup.

\`\`\`bash
git clone https://github.com/jjckarthikeyan-dot/scadova-ai-india.git
cd scadova-ai-india
python -m venv .venv
\`\`\`

Activate the environment:

- macOS/Linux: \`source .venv/bin/activate\`
- Windows PowerShell: \`.venv\Scripts\Activate.ps1\`

Then:

\`\`\`bash
pip install -r requirements.txt
cp .env.example .env
\`\`\`

Review and configure the values in \`.env\`. Never commit real keys or customer information.

\`\`\`bash
alembic upgrade head
uvicorn backend.main:app --reload
\`\`\`

Local documentation is expected at http://localhost:8000/docs when the application starts successfully.

## Testing

\`\`\`bash
pytest -v
\`\`\`

Run the suite locally or in CI before reporting a passing test count. No passing-test claim is made in this document without current execution evidence.

## Security and compliance considerations

Financial and identity data require careful handling. Before using this project with real applicant information, validate authorization and tenant isolation, secure credential storage, encryption and access control, sensitive-data redaction, and relevant legal and compliance obligations. A documented masking strategy does not by itself establish regulatory compliance.

## Additional documentation

- [API reference](docs/API.md)
- [Database design](docs/DATABASE.md)

## Author

[Karthikeyan Jammalamadaka](https://github.com/jjckarthikeyan-dot)
