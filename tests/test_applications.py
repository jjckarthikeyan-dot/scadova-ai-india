from decimal import Decimal


def test_application_lifecycle_and_analysis(client):
    # 1. Create Application (Personal Loan)
    create_payload = {
        "loan_type": "PERSONAL_LOAN",
        "requested_amount": 500000.00,
        "preferred_tenure_months": 36,
        "loan_purpose": "Home Renovation",
        "applicant": {
            "first_name": "Rohan",
            "last_name": "Sharma",
            "email": "rohan.sharma@example.com",
            "phone": "9876543210",
            "pan": "ABCDE1234F",
            "aadhaar": "987654321098",
            "date_of_birth": "1988-06-20",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560001",
        },
    }
    create_res = client.post("/api/loan-agency/applications", json=create_payload)
    assert create_res.status_code == 201
    app_data = create_res.json()["data"]
    app_id = app_data["id"]
    assert app_data["loan_type"] == "PERSONAL_LOAN"
    assert app_data["status"] == "DRAFT"

    # 2. Get Application
    get_res = client.get(f"/api/loan-agency/applications/{app_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == app_id

    # 3. Check Missing Fields before profile update
    missing_res = client.get(f"/api/loan-agency/applications/{app_id}/missing-fields")
    assert missing_res.status_code == 200
    assert "employment.company_name" in missing_res.json()["data"]["missing_fields"]

    # 4. Update Personal Loan Profile
    pl_payload = {
        "employment_type": "Salaried",
        "company_name": "Infosys Ltd",
        "designation": "Senior Tech Lead",
        "total_work_experience_years": 8.5,
        "current_company_joining_date": "2020-03-01",
        "industry_category": "IT",
        "gross_salary_monthly": 120000.00,
        "net_salary_monthly": 95000.00,
        "salary_credit_date": 30,
        "annual_income": 1440000.00,
        "other_income": 0.0,
        "average_bank_balance": 80000.00,
        "existing_personal_loans_count": 0,
        "credit_card_outstanding": 12000.00,
        "existing_monthly_emi": 15000.00,
        "cibil_score": 790,
        "has_overdues": False,
        "has_settlements": False,
        "has_write_offs": False,
        "balance_transfer_requirement": False,
    }
    pl_res = client.put(f"/api/loan-agency/personal-loans/{app_id}", json=pl_payload)
    assert pl_res.status_code == 200
    assert pl_res.json()["data"]["company_name"] == "Infosys Ltd"

    # 5. Document Presign and Complete
    presign_payload = {
        "document_type": "PAN",
        "file_name": "pan_card.pdf",
        "content_type": "application/pdf",
    }
    presign_res = client.post(f"/api/loan-agency/documents/{app_id}/presign", json=presign_payload)
    assert presign_res.status_code == 200
    storage_path = presign_res.json()["data"]["storage_path"]

    complete_payload = {
        "document_type": "PAN",
        "file_name": "pan_card.pdf",
        "storage_path": storage_path,
        "mime_type": "application/pdf",
        "file_size_bytes": 102400,
    }
    comp_res = client.post(f"/api/loan-agency/documents/{app_id}/complete", json=complete_payload)
    assert comp_res.status_code == 201
    doc_id = comp_res.json()["data"]["id"]

    # List documents
    docs_res = client.get(f"/api/loan-agency/documents/{app_id}")
    assert docs_res.status_code == 200
    assert len(docs_res.json()["data"]) >= 1

    # 6. Run Analysis
    analysis_res = client.post(f"/api/loan-agency/analysis/{app_id}")
    assert analysis_res.status_code == 200
    analysis_data = analysis_res.json()["data"]
    assert "rule_outcome" in analysis_data
    assert "calculated_emi" in analysis_data
    assert "foir_after_percentage" in analysis_data
    assert "disclaimer" in analysis_data

    # 7. Get Latest Analysis
    latest_res = client.get(f"/api/loan-agency/analysis/{app_id}/latest")
    assert latest_res.status_code == 200
    assert latest_res.json()["data"]["application_id"] == app_id

    # 8. Status Transition
    status_res = client.post(
        f"/api/loan-agency/applications/{app_id}/status",
        json={"new_status": "LENDER_SUBMITTED", "remarks": "Submitted to HDFC Bank"},
    )
    assert status_res.status_code == 200
    assert status_res.json()["data"]["status"] == "LENDER_SUBMITTED"

    # 9. Clean up document
    del_doc = client.delete(f"/api/loan-agency/documents/{app_id}/{doc_id}")
    assert del_doc.status_code == 200


def test_business_and_used_car_loans(client):
    # Business Loan Flow
    bus_app = client.post(
        "/api/loan-agency/applications",
        json={
            "loan_type": "BUSINESS_LOAN",
            "requested_amount": 2500000.00,
            "preferred_tenure_months": 36,
            "applicant": {
                "first_name": "Priya",
                "last_name": "Patel",
                "email": "priya@enterprise.in",
                "phone": "9823456789",
                "pan": "ABCDE5678G",
            },
        },
    ).json()["data"]

    bus_profile_res = client.put(
        f"/api/loan-agency/business-loans/{bus_app['id']}",
        json={
            "business_name": "Patel Enterprises",
            "entity_type": "Private Limited",
            "business_starting_year": 2018,
            "business_nature": "Manufacturing",
            "gst_status": "REGISTERED",
            "gstin": "27ABCDE1234F1Z5",
            "previous_year_turnover": 8500000.00,
            "current_fy_turnover": 9200000.00,
            "average_monthly_bank_credits": 750000.00,
            "existing_business_loans_count": 1,
            "current_outstanding": 500000.00,
            "existing_monthly_emi": 22000.00,
            "net_profit_annual": 1200000.00,
            "cibil_score": 760,
        },
    )
    assert bus_profile_res.status_code == 200
    assert bus_profile_res.json()["data"]["business_name"] == "Patel Enterprises"

    # Used Car Loan Flow
    car_app = client.post(
        "/api/loan-agency/applications",
        json={
            "loan_type": "USED_CAR_LOAN",
            "requested_amount": 600000.00,
            "preferred_tenure_months": 48,
            "applicant": {
                "first_name": "Vikram",
                "last_name": "Singh",
                "email": "vikram@example.com",
                "phone": "9811122233",
                "pan": "ABCDE9999K",
            },
        },
    ).json()["data"]

    car_profile_res = client.put(
        f"/api/loan-agency/used-car-loans/{car_app['id']}",
        json={
            "vehicle_make": "Hyundai",
            "model": "Creta",
            "variant": "SX Petrol",
            "manufacturing_year": 2021,
            "registration_year": 2021,
            "registration_number": "KA01MJ1234",
            "fuel_type": "PETROL",
            "transmission": "AUTOMATIC",
            "owner_number": 1,
            "kilometres_driven": 35000,
            "market_value": 850000.00,
            "valuation_amount": 800000.00,
            "purchase_price": 820000.00,
            "down_payment": 220000.00,
            "dealer_or_direct_seller": "DEALER",
            "monthly_income": 80000.00,
            "cibil_score": 770,
            "existing_monthly_emi": 5000.00,
        },
    )
    assert car_profile_res.status_code == 200
    assert car_profile_res.json()["data"]["vehicle_make"] == "Hyundai"
