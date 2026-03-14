import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey, UniqueConstraint, event
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

class CoreMasterBase(Base):
    """Abstract base class for all standard Meta-Engine tables."""
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    modified_by = Column(UUID(as_uuid=True), nullable=True)

class Company(CoreMasterBase):
    __tablename__ = "hr_companies"

    company_name = Column(String, nullable=False, unique=True, index=True)
    abbr = Column(String, nullable=False, unique=True)
    domain = Column(String, nullable=True)

    gstin = Column(String(15), nullable=True,
        comment="GST Identification Number. 15-char alphanumeric. "
                "Required for Indian GST compliance on invoices.")

    state_code = Column(String(2), nullable=True,
        comment="Two-letter Indian state code for CGST/SGST vs IGST "
                "determination. e.g. MH=Maharashtra, KA=Karnataka. "
                "Leave null for non-Indian companies.")

    base_currency_id = Column(UUID(as_uuid=True),
        ForeignKey("hr_currencies.id", ondelete="SET NULL"),
        nullable=True,
        comment="The company's reporting currency. "
                "All invoice amounts are converted to this currency "
                "for financial reporting.")

class Branch(CoreMasterBase):
    __tablename__ = "hr_branches"

    branch = Column(String, nullable=False, unique=True, index=True)

class Gender(CoreMasterBase):
    __tablename__ = "hr_genders"

    name = Column(String, nullable=False, unique=True, index=True)

class Salutation(CoreMasterBase):
    __tablename__ = "hr_salutations"

    name = Column(String, nullable=False, unique=True, index=True)

class EmploymentType(CoreMasterBase):
    __tablename__ = "hr_employment_types"

    employee_type_name = Column(String, nullable=False, unique=True, index=True)

class Designation(CoreMasterBase):
    __tablename__ = "hr_designations"

    designation_name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

class Skill(CoreMasterBase):
    __tablename__ = "hr_skills"

    skill_name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

class Currency(CoreMasterBase):
    __tablename__ = "hr_currencies"

    currency_code = Column(String, nullable=False, unique=True, index=True)
    currency_symbol = Column(String, nullable=True)
    fraction = Column(String, nullable=True)
    fraction_units = Column(Integer, default=100)

class User(CoreMasterBase):
    __tablename__ = "hr_users"

    email = Column(String, nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Authentication
    hashed_password = Column(String, nullable=True,
        comment="Bcrypt hashed password. Nullable because invite flow "
                "sets password after account creation.")

    # Role — determines module access and VEDA behaviour
    role = Column(String, nullable=False, default="employee",
        comment="One of: owner, hr_manager, finance_manager, "
                "manager, employee, auditor")

    # Org placement — links user to their position in the company
    company_id = Column(UUID(as_uuid=True),
        ForeignKey("hr_companies.id", ondelete="SET NULL"),
        nullable=True, index=True,
        comment="Which company this user belongs to within the tenant.")

    # Circular FK: User → Employee → User
    # use_alter=True defers FK creation to after both tables exist
    employee_id = Column(UUID(as_uuid=True),
        ForeignKey("hr_employees.id", ondelete="SET NULL",
                   use_alter=True, name="fk_user_employee_id"),
        nullable=True,
        comment="The employee record for this user. "
                "Null for owner accounts created before an employee record exists.")

    # Seat tracking
    last_login = Column(DateTime(timezone=True), nullable=True,
        comment="Last successful login timestamp. Used for seat activity tracking.")

class RolePermission(CoreMasterBase):
    """
    Defines what each role can do in each module.
    One row per role per module combination.
    Seeded with sensible defaults. Can be overridden per tenant.
    Used by require_permission() at runtime.
    """
    __tablename__ = "hr_role_permissions"

    role = Column(String, nullable=False, index=True,
        comment="One of: owner, hr_manager, finance_manager, "
                "manager, employee, auditor")

    module = Column(String, nullable=False, index=True,
        comment="One of: hrms, payroll, finance, settings, crm, tasks")

    can_view = Column(Boolean, default=False, nullable=False)
    can_create = Column(Boolean, default=False, nullable=False)
    can_edit = Column(Boolean, default=False, nullable=False)
    can_submit = Column(Boolean, default=False, nullable=False)
    can_approve = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'role', 'module',
                         name='uq_role_permission_per_tenant'),
    )

# --- Event Listeners for Automated Audit Logging ---

@event.listens_for(CoreMasterBase, 'before_insert', propagate=True)
def set_created_by(mapper, connection, target):
    from app.db.database import current_user_id_ctx
    user_id = current_user_id_ctx.get()
    if user_id:
        target.created_by = user_id
        target.modified_by = user_id

@event.listens_for(CoreMasterBase, 'before_update', propagate=True)
def set_modified_by(mapper, connection, target):
    from app.db.database import current_user_id_ctx
    user_id = current_user_id_ctx.get()
    if user_id:
        target.modified_by = user_id

