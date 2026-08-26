from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from backend.core.security import mask_pan, mask_aadhaar, mask_mobile
from backend.loan_agency.models import (
    Applicant,
    LoanApplication,
    BusinessProfile,
    EmploymentProfile,
    VehicleProfile,
    FinancialProfile,
    CreditProfile,
    BankAccount,
    Document,
    AnalysisRun,
    StatusHistory,
)
from backend.loan_agency.schemas import (
    LoanApplicationCreate,
    LoanApplicationUpdate,
    BusinessLoanProfileUpdate,
    PersonalLoanProfileUpdate,
    UsedCarLoanProfileUpdate,
    ApplicationStatusEnum,
)


class LoanAgencyRepository:
    """Repository handling all database CRUD operations for Loan Agency."""

    # -------------------------------------------------------------
    # Applications
    # -------------------------------------------------------------
    @staticmethod
    def create_application(db: Session, data: LoanApplicationCreate, tenant_id: str = "default") -> LoanApplication:
        # Create or find applicant
        applicant = Applicant(
            tenant_id=tenant_id,
            first_name=data.applicant.first_name,
            last_name=data.applicant.last_name,
            email=data.applicant.email,
            phone=mask_mobile(data.applicant.phone) or data.applicant.phone,
            pan_masked=mask_pan(data.applicant.pan) if data.applicant.pan else None,
            aadhaar_masked=mask_aadhaar(data.applicant.aadhaar) if data.applicant.aadhaar else None,
            date_of_birth=data.applicant.date_of_birth,
            gender=data.applicant.gender,
            current_address=data.applicant.current_address,
            city=data.applicant.city,
            state=data.applicant.state,
            pincode=data.applicant.pincode,
        )
        db.add(applicant)
        db.flush()

        import uuid
        app_num = f"SCA-{data.loan_type.value[:2]}-{uuid.uuid4().hex[:8].upper()}"

        application = LoanApplication(
            tenant_id=tenant_id,
            applicant_id=applicant.id,
            application_number=app_num,
            loan_type=data.loan_type.value,
            status=ApplicationStatusEnum.DRAFT.value,
            requested_amount=data.requested_amount,
            preferred_tenure_months=data.preferred_tenure_months,
            loan_purpose=data.loan_purpose,
        )
        db.add(application)
        db.flush()

        # Add initial status history
        history = StatusHistory(
            application_id=application.id,
            from_status="NONE",
            to_status=ApplicationStatusEnum.DRAFT.value,
            remarks="Application initialized in Draft status",
        )
        db.add(history)
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def get_application(db: Session, application_id: str) -> Optional[LoanApplication]:
        return db.query(LoanApplication).filter(LoanApplication.id == application_id).first()

    @staticmethod
    def get_application_by_number(db: Session, application_number: str) -> Optional[LoanApplication]:
        return db.query(LoanApplication).filter(LoanApplication.application_number == application_number).first()

    @staticmethod
    def list_applications(
        db: Session,
        tenant_id: Optional[str] = None,
        loan_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[LoanApplication]:
        query = db.query(LoanApplication)
        if tenant_id:
            query = query.filter(LoanApplication.tenant_id == tenant_id)
        if loan_type:
            query = query.filter(LoanApplication.loan_type == loan_type)
        if status:
            query = query.filter(LoanApplication.status == status)
        return query.order_by(LoanApplication.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_applications(
        db: Session,
        tenant_id: Optional[str] = None,
        loan_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        query = db.query(LoanApplication)
        if tenant_id:
            query = query.filter(LoanApplication.tenant_id == tenant_id)
        if loan_type:
            query = query.filter(LoanApplication.loan_type == loan_type)
        if status:
            query = query.filter(LoanApplication.status == status)
        return query.count()

    @staticmethod
    def update_application(db: Session, application_id: str, data: LoanApplicationUpdate) -> Optional[LoanApplication]:
        app = LoanAgencyRepository.get_application(db, application_id)
        if not app:
            return None
        if data.requested_amount is not None:
            app.requested_amount = data.requested_amount
        if data.preferred_tenure_months is not None:
            app.preferred_tenure_months = data.preferred_tenure_months
        if data.loan_purpose is not None:
            app.loan_purpose = data.loan_purpose
        if data.assigned_agent_id is not None:
            app.assigned_agent_id = data.assigned_agent_id
        db.commit()
        db.refresh(app)
        return app

    @staticmethod
    def delete_application(db: Session, application_id: str) -> bool:
        app = LoanAgencyRepository.get_application(db, application_id)
        if not app:
            return False
        db.delete(app)
        db.commit()
        return True

    # -------------------------------------------------------------
    # Status Transition
    # -------------------------------------------------------------
    @staticmethod
    def update_status(
        db: Session,
        application_id: str,
        new_status: str,
        user_id: Optional[str] = None,
        remarks: Optional[str] = None,
    ) -> Optional[LoanApplication]:
        app = LoanAgencyRepository.get_application(db, application_id)
        if not app:
            return None
        old_status = app.status
        app.status = new_status
        history = StatusHistory(
            application_id=app.id,
            from_status=old_status,
            to_status=new_status,
            changed_by_user_id=user_id,
            remarks=remarks,
        )
        db.add(history)
        db.commit()
        db.refresh(app)
        return app

    # -------------------------------------------------------------
    # Product Specific Profiles
    # -------------------------------------------------------------
    @staticmethod
    def save_business_profile(
        db: Session, application_id: str, data: BusinessLoanProfileUpdate
    ) -> BusinessProfile:
        profile = db.query(BusinessProfile).filter(BusinessProfile.application_id == application_id).first()
        if not profile:
            profile = BusinessProfile(application_id=application_id, business_name=data.business_name, entity_type=data.entity_type, business_starting_year=data.business_starting_year)
            db.add(profile)

        profile.business_name = data.business_name
        profile.entity_type = data.entity_type
        profile.business_starting_year = data.business_starting_year
        profile.business_nature = data.business_nature
        profile.business_address = data.business_address
        profile.gst_status = data.gst_status
        if data.gstin:
            profile.gstin_masked = f"{data.gstin[:2]}******{data.gstin[-3:]}" if len(data.gstin) >= 5 else "******"
        profile.udyam_msme_status = data.udyam_msme_status
        profile.previous_year_turnover = data.previous_year_turnover
        profile.current_fy_turnover = data.current_fy_turnover
        profile.average_monthly_bank_credits = data.average_monthly_bank_credits
        profile.existing_business_loans_count = data.existing_business_loans_count
        profile.current_outstanding = data.current_outstanding
        profile.existing_monthly_emi = data.existing_monthly_emi
        profile.net_profit_annual = data.net_profit_annual
        profile.liability_takeover_requirement = data.liability_takeover_requirement
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def save_personal_profile(
        db: Session, application_id: str, data: PersonalLoanProfileUpdate
    ) -> EmploymentProfile:
        profile = db.query(EmploymentProfile).filter(EmploymentProfile.application_id == application_id).first()
        if not profile:
            profile = EmploymentProfile(
                application_id=application_id,
                company_name=data.company_name,
                designation=data.designation,
                employment_type=data.employment_type,
            )
            db.add(profile)

        profile.company_name = data.company_name
        profile.designation = data.designation
        profile.employment_type = data.employment_type
        profile.total_work_experience_years = data.total_work_experience_years
        profile.current_company_joining_date = data.current_company_joining_date
        profile.industry_category = data.industry_category
        profile.gross_salary_monthly = data.gross_salary_monthly
        profile.net_salary_monthly = data.net_salary_monthly
        profile.salary_credit_date = data.salary_credit_date
        profile.annual_income = data.annual_income
        profile.other_income = data.other_income
        profile.existing_personal_loans_count = data.existing_personal_loans_count
        profile.credit_card_outstanding = data.credit_card_outstanding
        profile.existing_monthly_emi = data.existing_monthly_emi
        profile.balance_transfer_requirement = data.balance_transfer_requirement
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def save_vehicle_profile(
        db: Session, application_id: str, data: UsedCarLoanProfileUpdate
    ) -> VehicleProfile:
        profile = db.query(VehicleProfile).filter(VehicleProfile.application_id == application_id).first()
        if not profile:
            profile = VehicleProfile(
                application_id=application_id,
                vehicle_make=data.vehicle_make,
                model=data.model,
                manufacturing_year=data.manufacturing_year,
                registration_year=data.registration_year,
            )
            db.add(profile)

        profile.vehicle_make = data.vehicle_make
        profile.model = data.model
        profile.variant = data.variant
        profile.manufacturing_year = data.manufacturing_year
        profile.registration_year = data.registration_year
        if data.registration_number:
            reg = data.registration_number.strip().upper()
            profile.registration_number_masked = f"{reg[:4]}****{reg[-4:]}" if len(reg) >= 8 else "****"
        profile.fuel_type = data.fuel_type
        profile.transmission = data.transmission
        profile.owner_number = data.owner_number
        profile.kilometres_driven = data.kilometres_driven
        profile.insurance_validity_date = data.insurance_validity_date
        profile.rc_status = data.rc_status
        profile.accident_history = data.accident_history
        profile.market_value = data.market_value
        profile.valuation_amount = data.valuation_amount
        profile.purchase_price = data.purchase_price
        profile.down_payment = data.down_payment
        profile.dealer_or_direct_seller = data.dealer_or_direct_seller
        profile.refinance_or_bt_requirement = data.refinance_or_bt_requirement
        db.commit()
        db.refresh(profile)
        return profile

    # -------------------------------------------------------------
    # Documents
    # -------------------------------------------------------------
    @staticmethod
    def save_document(
        db: Session,
        application_id: str,
        document_type: str,
        file_name: str,
        storage_path: str,
        mime_type: str,
        file_size_bytes: Optional[int] = None,
    ) -> Document:
        doc = Document(
            application_id=application_id,
            document_type=document_type,
            file_name=file_name,
            storage_path=storage_path,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            verification_status="PENDING",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def get_documents_by_application(db: Session, application_id: str) -> List[Document]:
        return db.query(Document).filter(Document.application_id == application_id).all()

    @staticmethod
    def delete_document(db: Session, application_id: str, document_id: str) -> bool:
        doc = db.query(Document).filter(Document.application_id == application_id, Document.id == document_id).first()
        if not doc:
            return False
        db.delete(doc)
        db.commit()
        return True

    # -------------------------------------------------------------
    # Analysis Runs
    # -------------------------------------------------------------
    @staticmethod
    def save_analysis_run(db: Session, application_id: str, run_data: Dict[str, Any]) -> AnalysisRun:
        analysis = AnalysisRun(
            application_id=application_id,
            rule_outcome=run_data["rule_outcome"],
            eligible_amount=run_data["eligible_amount"],
            calculated_emi=run_data["calculated_emi"],
            foir_before=run_data["foir_before"],
            foir_after=run_data["foir_after"],
            ltv_percentage=run_data.get("ltv_percentage"),
            rule_reason_codes=run_data.get("rule_reason_codes", []),
            missing_information=run_data.get("missing_information", []),
            strengths=run_data.get("strengths", []),
            risk_factors=run_data.get("risk_factors", []),
            recommended_lender_category=run_data.get("recommended_lender_category", "PRIME_BANK"),
            ai_summary=run_data.get("ai_summary"),
            disclaimer=run_data.get("disclaimer"),
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def get_latest_analysis_run(db: Session, application_id: str) -> Optional[AnalysisRun]:
        return (
            db.query(AnalysisRun)
            .filter(AnalysisRun.application_id == application_id)
            .order_by(AnalysisRun.created_at.desc())
            .first()
        )
