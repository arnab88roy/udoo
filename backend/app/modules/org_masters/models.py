import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.modules.core_masters.models import CoreMasterBase

class Department(CoreMasterBase):
    __tablename__ = "hr_departments"

    department_name = Column(String, nullable=False, unique=True, index=True)
    parent_department = Column(UUID(as_uuid=True), ForeignKey("hr_departments.id", ondelete="SET NULL"), nullable=True)
    company = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="CASCADE"), nullable=False, index=True)
    is_group = Column(Boolean, default=False, nullable=False)
    disabled = Column(Boolean, default=False, nullable=False)

    # Relationships
    company_rel = relationship("Company", foreign_keys=[company])
    parent_rel = relationship("Department", remote_side="Department.id", backref="children")

class EmployeeGrade(CoreMasterBase):
    __tablename__ = "hr_employee_grades"

    grade_name = Column(String, nullable=False, unique=True, index=True)
    default_base_pay = Column(Numeric(18, 2), nullable=True)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("hr_currencies.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    currency_rel = relationship("Currency")

