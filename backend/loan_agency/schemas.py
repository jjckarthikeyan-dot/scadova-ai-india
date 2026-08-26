from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoanProductEnum(str, Enum):
    BUSINESS_LOAN = "BUSINESS_LOAN"
    PERSONAL_LOAN = "PERSONAL_LOAN"
    USED_CAR_LOAN = "USED_CAR_LOAN"


class ApplicationStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    DATA_PENDING = "DATA_PENDING"
    DOCUMENTS_PENDING = "DOCUMENTS_PENDING"
    READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    REFERRED = "REFERRED"
    DECLINED = "DECLINED"
    LENDER_SUBMITTED = "LENDER_SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class RuleOutcomeEnum(str, Enum):
    PASS = "PASS"
    REFER = "REFER"
    DECLINE = "DECLINE"
    DATA_REQUIRED = "DATA_REQUIRED"


class DocumentTypeEnum(str, Enum):
    PAN = "PAN"
    AADHAAR = "AADHAAR"
    BANK_STATEMENTS = "BANK_STATEMENTS"
    SALARY_SLIPS = "SALARY_SLIPS"
    ITR = "ITR"
    FORM_16 = "FORM_16"
    GST_CERTIFICATE = "GST_CERTIFICATE"
    GST_RETURNS = "GST_RETURNS"
    BUSINESS_REGISTRATION = "BUSINESS_REGISTRATION"
    FINANCIAL_STATEMENTS = "FINANCIAL_STATEMENTS"
    RC = "RC"
    INSURANCE = "INSURANCE"
    VALUATION_REPORT = "VALUATION_REPORT"
    SELLER_QUOTATION = "SELLER_QUOTATION"
    OTHER = "OTHER"


# -------------------------------------------------------------
# Base Applicant Schemas
# -------------------------------------------------------------

class ApplicantBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=255)
    phone: str = Field(..., min_length=10, max_length=15)
    pan: Optional[str] = Field(None, description="Unmasked PAN (will be securely masked)")
    aadhaar: Optional[str] = Field(None, description="Aadhaar (will be masked)")
    date_of_birth: Optional[str] = None  # YYYY-MM-DD
    gender: Optional[str] = None
    current_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


class ApplicantCreate(ApplicantBase):
    pass


class ApplicantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    pan_masked: Optional[str] = None
    aadhaar_masked: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    current_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    created_at: datetime


# -------------------------------------------------------------
# Business Loan Profile Schemas
# -------------------------------------------------------------

class BusinessLoanProfileUpdate(BaseModel):
    business_name: str
    entity_type: str = Field(..., description="Proprietorship, Partnership, Pvt Ltd, LLP")
    business_starting_year: int
    business_nature: Optional[str] = None
    business_address: Optional[str] = None
    gst_status: str = Field(default="REGISTERED", description="REGISTERED or UNREGISTERED")
    gstin: Optional[str] = None
    udyam_msme_status: str = Field(default="REGISTERED")
    previous_year_turnover: Decimal = Field(default=Decimal("0.0"), ge=0)
    current_fy_turnover: Decimal = Field(default=Decimal("0.0"), ge=0)
    average_monthly_bank_credits: Decimal = Field(default=Decimal("0.0"), ge=0)
    existing_business_loans_count: int = Field(default=0, ge=0)
    current_outstanding: Decimal = Field(default=Decimal("0.0"), ge=0)
    existing_monthly_emi: Decimal = Field(default=Decimal("0.0"), ge=0)
    net_profit_annual: Decimal = Field(default=Decimal("0.0"))
    cibil_score: int = Field(default=750, ge=300, le=900)
    has_overdues: bool = False
    has_settlements: bool = False
    has_write_offs: bool = False
    cheque_emi_bounces_last_6m: int = Field(default=0, ge=0)
    statement_coverage_months: int = Field(default=6, ge=1)
    liability_takeover_requirement: bool = False


class BusinessLoanProfileRead(BusinessLoanProfileUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    gstin_masked: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# -------------------------------------------------------------
# Personal Loan Profile Schemas
# -------------------------------------------------------------

class PersonalLoanProfileUpdate(BaseModel):
    employment_type: str = Field(default="Salaried", description="Salaried, Self-Employed Professional")
    company_name: str
    designation: str
    total_work_experience_years: Decimal = Field(default=Decimal("1.0"), ge=0)
    current_company_joining_date: Optional[str] = None  # YYYY-MM-DD
    industry_category: str = Field(default="IT")
    gross_salary_monthly: Decimal = Field(default=Decimal("0.0"), ge=0)
    net_salary_monthly: Decimal = Field(default=Decimal("0.0"), ge=0)
    salary_credit_date: int = Field(default=1, ge=1, le=31)
    annual_income: Decimal = Field(default=Decimal("0.0"), ge=0)
    other_income: Decimal = Field(default=Decimal("0.0"), ge=0)
    average_bank_balance: Decimal = Field(default=Decimal("0.0"), ge=0)
    existing_personal_loans_count: int = Field(default=0, ge=0)
    credit_card_outstanding: Decimal = Field(default=Decimal("0.0"), ge=0)
    existing_monthly_emi: Decimal = Field(default=Decimal("0.0"), ge=0)
    cibil_score: int = Field(default=750, ge=300, le=900)
    has_overdues: bool = False
    has_settlements: bool = False
    has_write_offs: bool = False
    balance_transfer_requirement: bool = False


class PersonalLoanProfileRead(PersonalLoanProfileUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    created_at: datetime
    updated_at: datetime


# -------------------------------------------------------------
# Used Car Loan Profile Schemas
# -------------------------------------------------------------

class UsedCarLoanProfileUpdate(BaseModel):
    # Vehicle details
    vehicle_make: str
    model: str
    variant: Optional[str] = None
    manufacturing_year: int = Field(..., ge=2000, le=2030)
    registration_year: int = Field(..., ge=2000, le=2030)
    registration_number: Optional[str] = None
    fuel_type: str = Field(default="PETROL")
    transmission: str = Field(default="MANUAL")
    owner_number: int = Field(default=1, ge=1, le=10)
    kilometres_driven: int = Field(default=0, ge=0)
    insurance_validity_date: Optional[str] = None
    rc_status: str = Field(default="VALID")
    accident_history: bool = False
    market_value: Decimal = Field(default=Decimal("0.0"), ge=0)
    valuation_amount: Decimal = Field(default=Decimal("0.0"), ge=0)
    purchase_price: Decimal = Field(default=Decimal("0.0"), ge=0)
    down_payment: Decimal = Field(default=Decimal("0.0"), ge=0)
    dealer_or_direct_seller: str = Field(default="DEALER")
    refinance_or_bt_requirement: bool = False
    # Financials
    monthly_income: Decimal = Field(default=Decimal("0.0"), ge=0)
    cibil_score: int = Field(default=750, ge=300, le=900)
    existing_monthly_emi: Decimal = Field(default=Decimal("0.0"), ge=0)
    has_overdues: bool = False
    has_settlements: bool = False


class UsedCarLoanProfileRead(UsedCarLoanProfileUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    registration_number_masked: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# -------------------------------------------------------------
# Application Core Schemas
# -------------------------------------------------------------

class LoanApplicationCreate(BaseModel):
    loan_type: LoanProductEnum
    requested_amount: Decimal = Field(..., gt=0)
    preferred_tenure_months: int = Field(..., ge=6, le=360)
    loan_purpose: Optional[str] = None
    applicant: ApplicantCreate


class LoanApplicationUpdate(BaseModel):
    requested_amount: Optional[Decimal] = Field(None, gt=0)
    preferred_tenure_months: Optional[int] = Field(None, ge=6, le=360)
    loan_purpose: Optional[str] = None
    assigned_agent_id: Optional[str] = None


class StatusTransitionRequest(BaseModel):
    new_status: ApplicationStatusEnum
    remarks: Optional[str] = None


class LoanApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_number: str
    loan_type: LoanProductEnum
    status: ApplicationStatusEnum
    requested_amount: Decimal
    preferred_tenure_months: int
    loan_purpose: Optional[str] = None
    applicant_id: str
    applicant: Optional[ApplicantRead] = None
    business_profile: Optional[BusinessLoanProfileRead] = None
    employment_profile: Optional[PersonalLoanProfileRead] = None
    vehicle_profile: Optional[UsedCarLoanProfileRead] = None
    created_at: datetime
    updated_at: datetime


# -------------------------------------------------------------
# Documents Schemas
# -------------------------------------------------------------

class DocumentPresignRequest(BaseModel):
    document_type: DocumentTypeEnum
    file_name: str
    content_type: str = Field(default="application/pdf")
    file_size_bytes: Optional[int] = None


class DocumentPresignResponse(BaseModel):
    upload_url: str
    storage_path: str
    token: str
    expires_in: str


class DocumentCompleteRequest(BaseModel):
    document_type: DocumentTypeEnum
    file_name: str
    storage_path: str
    mime_type: str
    file_size_bytes: Optional[int] = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    document_type: str
    file_name: str
    storage_path: str
    mime_type: str
    file_size_bytes: Optional[int] = None
    verification_status: str
    download_url: Optional[str] = None
    uploaded_at: datetime


# -------------------------------------------------------------
# Analysis & Calculation Schemas
# -------------------------------------------------------------

class CalculationResult(BaseModel):
    emi: Decimal
    foir_before: Decimal
    foir_after: Decimal
    max_affordable_emi: Decimal
    indicative_eligible_principal: Decimal
    ltv_percentage: Optional[Decimal] = None
    required_down_payment: Optional[Decimal] = None


class RuleEvaluationResult(BaseModel):
    outcome: RuleOutcomeEnum
    triggered_rules: List[str]
    reason_codes: List[str]
    missing_fields: List[str]
    strengths: List[str]
    risk_factors: List[str]


class AnalysisResponse(BaseModel):
    application_id: str
    application_number: str
    loan_type: LoanProductEnum
    status: ApplicationStatusEnum
    rule_outcome: RuleOutcomeEnum
    indicative_eligible_amount: Decimal
    calculated_emi: Decimal
    foir_before_percentage: Decimal
    foir_after_percentage: Decimal
    ltv_percentage: Optional[Decimal] = None
    recommended_lender_category: str
    strengths: List[str]
    risk_factors: List[str]
    missing_information: List[str]
    rule_reason_codes: List[str]
    ai_summary: Optional[str] = None
    disclaimer: str
    timestamp: datetime
