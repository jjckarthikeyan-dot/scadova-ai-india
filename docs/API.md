# Scadova-AI-India API Documentation

## Overview
Scadova-AI-India provides an Indian retail and SME loan underwriting platform API.

- **Base URL**: `http://localhost:8000`
- **Prefix**: `/api/loan-agency`
- **OpenAPI / Swagger**: `/docs`
- **ReDoc**: `/redoc`

---

## 1. System Endpoints

### Root
- **GET `/`**
```json
{
  "success": true,
  "product": "Scadova-AI-India",
  "module": "loan_agency",
  "version": "1.0.0",
  "status": "running"
}
```

### Health Checks
- **GET `/health`**: Returns system health status.
- **GET `/health/live`**: Kubernetes liveness probe.
- **GET `/health/ready`**: Database readiness probe.

---

## 2. Loan Agency Module

### Home
- **GET `/api/loan-agency/`**

### Applications
- **POST `/api/loan-agency/applications`**: Create application in `DRAFT` status.
- **GET `/api/loan-agency/applications`**: List applications with filters (`loan_type`, `status`, `page`, `limit`).
- **GET `/api/loan-agency/applications/{id}`**: Get full application object.
- **PATCH `/api/loan-agency/applications/{id}`**: Update application details.
- **DELETE `/api/loan-agency/applications/{id}`**: Delete application.
- **GET `/api/loan-agency/applications/{id}/missing-fields`**: Inspect missing required fields.
- **POST `/api/loan-agency/applications/{id}/submit`**: Submit application for review.
- **POST `/api/loan-agency/applications/{id}/status`**: Transition workflow status.

### Products

#### Business Loans
- **PUT `/api/loan-agency/business-loans/{application_id}`**: Save business entity data, turnover, banking credits, and GST.
- **GET `/api/loan-agency/business-loans/{application_id}`**: Get business loan details.

#### Personal Loans
- **PUT `/api/loan-agency/personal-loans/{application_id}`**: Save employment details, monthly salary, experience, existing EMIs.
- **GET `/api/loan-agency/personal-loans/{application_id}`**: Get personal loan profile.

#### Used Car Loans
- **PUT `/api/loan-agency/used-car-loans/{application_id}`**: Save vehicle specifications, valuation, purchase price, down payment.
- **GET `/api/loan-agency/used-car-loans/{application_id}`**: Get vehicle profile.

---

## 3. Documents
- **POST `/api/loan-agency/documents/{application_id}/presign`**: Generate short-lived presigned upload URL.
- **POST `/api/loan-agency/documents/{application_id}/complete`**: Complete upload record.
- **GET `/api/loan-agency/documents/{application_id}`**: List uploaded documents with temporary signed download URLs.
- **DELETE `/api/loan-agency/documents/{application_id}/{document_id}`**: Delete document record.

---

## 4. Underwriting & Analysis
- **POST `/api/loan-agency/analysis/{application_id}`**: Run deterministic financial calculation and underwriting rule engine.
- **GET `/api/loan-agency/analysis/{application_id}/latest`**: Fetch latest analysis report.

---

## 5. Response Envelope

All API endpoints strictly follow the standard JSON response format:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "request_id": "8fa88d01-e234-406a-a25e-399081273934",
  "timestamp": "2026-08-26T12:00:00.000000+00:00"
}
```
