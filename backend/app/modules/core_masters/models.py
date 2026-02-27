import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
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

