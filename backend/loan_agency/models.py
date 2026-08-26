import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship

from backend.core.database import Base

# JSON type that works across PostgreSQL and SQLite
JSONType = SQLiteJSON


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(50), default="default", index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="AGENT", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(50), default="default", index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    pan_masked = Column(String(20), nullable=True)
    aadhaar_masked = Column(String(20), nullable=True)
    date_of_birth = Column(String(20), nullable=True)
    gender = Column(String(20), nullable=True)
    current_address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    applications = relationship("LoanApplication", back_populates="applicant")


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(50), default="default", index=True)
    applicant_id = Column(String(36), ForeignKey("applicants.id"), nullable=False, index=True)
    application_number = Column(String(50), unique=True, index=True, nullable=False)
    loan_type = Column(String(50), nullable=False, index=True)  # BUSINESS_LOAN, PERSONAL_LOAN, USED_CAR_LOAN
    status = Column(String(50), default="DRAFT", nullable=False, index=True)
    requested_amount = Column(Numeric(14, 2), nullable=False)
    preferred_tenure_months = Column(Integer, nullable=False)
    loan_purpose = Column(String(255), nullable=True)
    assigned_agent_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    applicant = relationship("Applicant", back_populates="applications")
    business_profile = relationship("BusinessProfile", back_populates="application", uselist=False, cascade="all, delete-orphan")
    employment_profile = relationship("EmploymentProfile", back_populates="application", uselist=False, cascade="all, delete-orphan")
    financial_profile = relationship("FinancialProfile", back_populates="application", uselist=False, cascade="all, delete-orphan")
    credit_profile = relationship("CreditProfile", back_populates="application", uselist=False, cascade="all, delete-orphan")
    vehicle_profile = relationship("VehicleProfile", back_populates="application", uselist=False, cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="application", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="application", cascade="all, delete-orphan")
    status_history = relationship("StatusHistory", back_populates="application", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="application", cascade="all, delete-orphan")


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), unique=True, nullable=False)
    business_name = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=False)  # Proprietorship, Partnership, Pvt Ltd, LLP
    business_starting_year = Column(Integer, nullable=False)
    business_nature = Column(String(255), nullable=True)
    business_address = Column(Text, nullable=True)
    gst_status = Column(String(50), default="REGISTERED")
    gstin_masked = Column(String(20), nullable=True)
    udyam_msme_status = Column(String(50), default="REGISTERED")
    previous_year_turnover = Column(Numeric(14, 2), default=0.0)
    current_fy_turnover = Column(Numeric(14, 2), default=0.0)
    average_monthly_bank_credits = Column(Numeric(14, 2), default=0.0)
    existing_business_loans_count = Column(Integer, default=0)
    current_outstanding = Column(Numeric(14, 2), default=0.0)
    existing_monthly_emi = Column(Numeric(14, 2), default=0.0)
    net_profit_annual = Column(Numeric(14, 2), default=0.0)
    liability_takeover_requirement = Column(Boolean, default=False)
    metadata_json = Column(JSONType, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    application = relationship("LoanApplication", back_populates="business_profile")


class EmploymentProfile(Base):
    __tablename__ = "employment_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), unique=True, nullable=False)
    employment_type = Column(String(100), nullable=False)  # Salaried, Self-Employed Professional
    company_name = Column(String(255), nullable=False)
    designation = Column(String(150), nullable=False)
    total_work_experience_years = Column(Numeric(4, 1), default=0.0)
    current_company_joining_date = Column(String(20), nullable=True)
    industry_category = Column(String(100), default="IT")  # IT, Banking, Manufacturing, etc.
    gross_salary_monthly = Column(Numeric(12, 2), default=0.0)
    net_salary_monthly = Column(Numeric(12, 2), default=0.0)
    salary_credit_date = Column(Integer, default=1)
    annual_income = Column(Numeric(14, 2), default=0.0)
    other_income = Column(Numeric(12, 2), default=0.0)
    existing_personal_loans_count = Column(Integer, default=0)
    credit_card_outstanding = Column(Numeric(12, 2), default=0.0)
    existing_monthly_emi = Column(Numeric(12, 2), default=0.0)
    balance_transfer_requirement = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    application = relationship("LoanApplication", back_populates="employment_profile")


class VehicleProfile(Base):
    __tablename__ = "vehicle_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), unique=True, nullable=False)
    vehicle_make = Column(String(100), nullable=False)  # Hyundai, Maruti, Honda, etc.
    model = Column(String(100), nullable=False)
    variant = Column(String(100), nullable=True)
    manufacturing_year = Column(Integer, nullable=False)
    registration_year = Column(Integer, nullable=False)
    registration_number_masked = Column(String(50), nullable=True)
    fuel_type = Column(String(50), default="PETROL")  # PETROL, DIESEL, CNG, ELECTRIC
    transmission = Column(String(50), default="MANUAL")  # MANUAL, AUTOMATIC
    owner_number = Column(Integer, default=1)
    kilometres_driven = Column(Integer, default=0)
    insurance_validity_date = Column(String(20), nullable=True)
    rc_status = Column(String(50), default="VALID")
    accident_history = Column(Boolean, default=False)
    market_value = Column(Numeric(12, 2), default=0.0)
    valuation_amount = Column(Numeric(12, 2), default=0.0)
    purchase_price = Column(Numeric(12, 2), default=0.0)
    down_payment = Column(Numeric(12, 2), default=0.0)
    dealer_or_direct_seller = Column(String(100), default="DEALER")
    refinance_or_bt_requirement = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    application = relationship("LoanApplication", back_populates="vehicle_profile")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), unique=True, nullable=False)
    average_monthly_income = Column(Numeric(14, 2), default=0.0)
    total_existing_monthly_obligations = Column(Numeric(14, 2), default=0.0)
    average_bank_balance = Column(Numeric(14, 2), default=0.0)
    statement_coverage_months = Column(Integer, default=6)
    cheque_emi_bounces_last_6m = Column(Integer, default=0)
    calculated_foir_current = Column(Numeric(6, 2), default=0.0)
    calculated_foir_proposed = Column(Numeric(6, 2), default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    application = relationship("LoanApplication", back_populates="financial_profile")


class CreditProfile(Base):
    __tablename__ = "credit_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), unique=True, nullable=False)
    cibil_score = Column(Integer, nullable=False, default=750)
    has_overdues = Column(Boolean, default=False)
    overdue_amount = Column(Numeric(12, 2), default=0.0)
    has_settlements = Column(Boolean, default=False)
    has_write_offs = Column(Boolean, default=False)
    credit_inquiries_last_30d = Column(Integer, default=0)
    cibil_report_date = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    application = relationship("LoanApplication", back_populates="credit_profile")


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), nullable=False, index=True)
    bank_name = Column(String(100), nullable=False)
    account_number_masked = Column(String(50), nullable=False)
    ifsc_code = Column(String(20), nullable=False)
    account_type = Column(String(50), default="SAVINGS")  # SAVINGS, CURRENT
    average_monthly_balance = Column(Numeric(12, 2), default=0.0)
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    application = relationship("LoanApplication", back_populates="bank_accounts")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), nullable=False, index=True)
    document_type = Column(String(100), nullable=False)  # PAN, AADHAAR, BANK_STATEMENT, SALARY_SLIP, etc.
    file_name = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    verification_status = Column(String(50), default="PENDING")  # PENDING, VERIFIED, REJECTED
    metadata_json = Column(JSONType, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=utc_now)

    application = relationship("LoanApplication", back_populates="documents")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), nullable=False, index=True)
    run_number = Column(Integer, default=1)
    rule_outcome = Column(String(50), nullable=False)  # PASS, REFER, DECLINE, DATA_REQUIRED
    eligible_amount = Column(Numeric(14, 2), default=0.0)
    calculated_emi = Column(Numeric(12, 2), default=0.0)
    foir_before = Column(Numeric(6, 2), default=0.0)
    foir_after = Column(Numeric(6, 2), default=0.0)
    ltv_percentage = Column(Numeric(6, 2), nullable=True)
    rule_reason_codes = Column(JSONType, default=list)
    missing_information = Column(JSONType, default=list)
    strengths = Column(JSONType, default=list)
    risk_factors = Column(JSONType, default=list)
    recommended_lender_category = Column(String(100), default="PRIME_BANK")
    ai_summary = Column(Text, nullable=True)
    disclaimer = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    application = relationship("LoanApplication", back_populates="analysis_runs")


class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), nullable=False, index=True)
    from_status = Column(String(50), nullable=False)
    to_status = Column(String(50), nullable=False)
    changed_by_user_id = Column(String(36), nullable=True)
    remarks = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now)

    application = relationship("LoanApplication", back_populates="status_history")


class Consent(Base):
    __tablename__ = "consents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("loan_applications.id"), nullable=False, index=True)
    consent_type = Column(String(100), nullable=False)  # CIBIL_FETCH, KYC_VERIFICATION, DATA_PROCESSING
    is_granted = Column(Boolean, default=True)
    ip_address = Column(String(50), nullable=True)
    granted_at = Column(DateTime(timezone=True), default=utc_now)

    application = relationship("LoanApplication", back_populates="consents")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(50), default="default", index=True)
    event_type = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(JSONType, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)
