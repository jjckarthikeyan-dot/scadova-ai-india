"""Initial database schema for Scadova-AI-India Loan Agency

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-26 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)

    # Applicants
    op.create_table(
        'applicants',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('pan_masked', sa.String(length=20), nullable=True),
        sa.Column('aadhaar_masked', sa.String(length=20), nullable=True),
        sa.Column('date_of_birth', sa.String(length=20), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('current_address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('pincode', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applicants_email'), 'applicants', ['email'], unique=False)
    op.create_index(op.f('ix_applicants_phone'), 'applicants', ['phone'], unique=False)
    op.create_index(op.f('ix_applicants_tenant_id'), 'applicants', ['tenant_id'], unique=False)

    # Loan Applications
    op.create_table(
        'loan_applications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('applicant_id', sa.String(length=36), nullable=False),
        sa.Column('application_number', sa.String(length=50), nullable=False),
        sa.Column('loan_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('requested_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('preferred_tenure_months', sa.Integer(), nullable=False),
        sa.Column('loan_purpose', sa.String(length=255), nullable=True),
        sa.Column('assigned_agent_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['applicant_id'], ['applicants.id'], ),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loan_applications_application_number'), 'loan_applications', ['application_number'], unique=True)
    op.create_index(op.f('ix_loan_applications_loan_type'), 'loan_applications', ['loan_type'], unique=False)
    op.create_index(op.f('ix_loan_applications_status'), 'loan_applications', ['status'], unique=False)

    # Business Profiles
    op.create_table(
        'business_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('business_starting_year', sa.Integer(), nullable=False),
        sa.Column('business_nature', sa.String(length=255), nullable=True),
        sa.Column('business_address', sa.Text(), nullable=True),
        sa.Column('gst_status', sa.String(length=50), nullable=True),
        sa.Column('gstin_masked', sa.String(length=20), nullable=True),
        sa.Column('udyam_msme_status', sa.String(length=50), nullable=True),
        sa.Column('previous_year_turnover', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('current_fy_turnover', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('average_monthly_bank_credits', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('existing_business_loans_count', sa.Integer(), nullable=True),
        sa.Column('current_outstanding', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('existing_monthly_emi', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('net_profit_annual', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('liability_takeover_requirement', sa.Boolean(), nullable=True),
        sa.Column('metadata_json', SQLiteJSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['loan_applications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id')
    )

    # Employment Profiles
    op.create_table(
        'employment_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('employment_type', sa.String(length=100), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('designation', sa.String(length=150), nullable=False),
        sa.Column('total_work_experience_years', sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column('current_company_joining_date', sa.String(length=20), nullable=True),
        sa.Column('industry_category', sa.String(length=100), nullable=True),
        sa.Column('gross_salary_monthly', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('net_salary_monthly', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('salary_credit_date', sa.Integer(), nullable=True),
        sa.Column('annual_income', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('other_income', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('existing_personal_loans_count', sa.Integer(), nullable=True),
        sa.Column('credit_card_outstanding', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('existing_monthly_emi', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('balance_transfer_requirement', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['loan_applications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id')
    )

    # Vehicle Profiles
    op.create_table(
        'vehicle_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('vehicle_make', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('variant', sa.String(length=100), nullable=True),
        sa.Column('manufacturing_year', sa.Integer(), nullable=False),
        sa.Column('registration_year', sa.Integer(), nullable=False),
        sa.Column('registration_number_masked', sa.String(length=50), nullable=True),
        sa.Column('fuel_type', sa.String(length=50), nullable=True),
        sa.Column('transmission', sa.String(length=50), nullable=True),
        sa.Column('owner_number', sa.Integer(), nullable=True),
        sa.Column('kilometres_driven', sa.Integer(), nullable=True),
        sa.Column('insurance_validity_date', sa.String(length=20), nullable=True),
        sa.Column('rc_status', sa.String(length=50), nullable=True),
        sa.Column('accident_history', sa.Boolean(), nullable=True),
        sa.Column('market_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('valuation_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('purchase_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('down_payment', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('dealer_or_direct_seller', sa.String(length=100), nullable=True),
        sa.Column('refinance_or_bt_requirement', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['loan_applications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id')
    )

    # Documents
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=True),
        sa.Column('metadata_json', SQLiteJSON(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['loan_applications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Analysis Runs
    op.create_table(
        'analysis_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('run_number', sa.Integer(), nullable=True),
        sa.Column('rule_outcome', sa.String(length=50), nullable=False),
        sa.Column('eligible_amount', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('calculated_emi', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('foir_before', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('foir_after', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('ltv_percentage', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('rule_reason_codes', SQLiteJSON(), nullable=True),
        sa.Column('missing_information', SQLiteJSON(), nullable=True),
        sa.Column('strengths', SQLiteJSON(), nullable=True),
        sa.Column('risk_factors', SQLiteJSON(), nullable=True),
        sa.Column('recommended_lender_category', sa.String(length=100), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('disclaimer', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['loan_applications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Status History
    op.create_table(
        'status_history',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('application_id', sa.String(length=36), nullable=False),
        sa.Column('from_status', sa.String(length=50), nullable=False),
        sa.Column('to_status', sa.String(length=50), nullable=False),
        sa.Column('changed_by_user_id', sa.String(length=36), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['loan_applications.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Audit Events
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('details', SQLiteJSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_events_event_type'), 'audit_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_events_created_at'), 'audit_events', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('status_history')
    op.drop_table('analysis_runs')
    op.drop_table('documents')
    op.drop_table('vehicle_profiles')
    op.drop_table('employment_profiles')
    op.drop_table('business_profiles')
    op.drop_table('loan_applications')
    op.drop_table('applicants')
    op.drop_table('users')
