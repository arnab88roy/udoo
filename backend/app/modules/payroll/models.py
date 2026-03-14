from sqlalchemy import Column, String, Boolean, Date, ForeignKey, Integer, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.modules.core_masters.models import CoreMasterBase

class ComplianceSettings(CoreMasterBase):
    """
    One record per company. Determines which statutory deductions apply.
    """
    __tablename__ = "hr_compliance_settings"

    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False, unique=True)
    pf_applicable = Column(Boolean, default=False, nullable=False)
    esi_applicable = Column(Boolean, default=False, nullable=False)
    pt_applicable = Column(Boolean, default=False, nullable=False)
    tds_applicable = Column(Boolean, default=True, nullable=False)
    pf_wage_ceiling = Column(Numeric(10, 2), default=15000.00, nullable=False)
    esi_gross_ceiling = Column(Numeric(10, 2), default=21000.00, nullable=False)

    # Relationships
    company = relationship("Company")

class ProfessionalTaxSlab(CoreMasterBase):
    """
    Configurable PT slabs per state. PT varies by state and by month (Feb is different in some states).
    """
    __tablename__ = "hr_professional_tax_slabs"

    state_code = Column(String(2), nullable=False)
    min_salary = Column(Numeric(10, 2), nullable=False)
    max_salary = Column(Numeric(10, 2), nullable=True)
    pt_amount = Column(Numeric(10, 2), nullable=False)
    is_february = Column(Boolean, default=False, nullable=False)
    effective_from = Column(Date, nullable=False)

class SalaryComponent(CoreMasterBase):
    """
    Master catalog of all earnings and deduction types.
    """
    __tablename__ = "hr_salary_components"

    component_name = Column(String(100), nullable=False)
    component_type = Column(String(20), nullable=False)  # Earning, Deduction, Employer Contribution, Informational
    is_statutory = Column(Boolean, default=False, nullable=False)
    is_taxable = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "component_name", name="uq_salary_component_name"),
    )

class SalaryStructure(CoreMasterBase):
    """
    Template that defines how salary is composed for a given role or employee.
    """
    __tablename__ = "hr_salary_structures"

    structure_name = Column(String(100), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    company = relationship("Company")
    components = relationship("SalaryStructureComponent", back_populates="salary_structure", cascade="all, delete-orphan")

class SalaryStructureComponent(CoreMasterBase):
    """
    Child table — links components to a structure with calculation rules.
    """
    __tablename__ = "hr_salary_structure_components"

    salary_structure_id = Column(UUID(as_uuid=True), ForeignKey("hr_salary_structures.id", ondelete="CASCADE"), nullable=False)
    salary_component_id = Column(UUID(as_uuid=True), ForeignKey("hr_salary_components.id", ondelete="RESTRICT"), nullable=False)
    calculation_type = Column(String(20), nullable=False)  # Fixed, Percentage of Basic, Percentage of Gross, Statutory
    value = Column(Numeric(10, 4), nullable=False)
    order_index = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("salary_structure_id", "salary_component_id", name="uq_structure_component"),
    )

    # Relationships
    salary_structure = relationship("SalaryStructure", back_populates="components")
    salary_component = relationship("SalaryComponent")

class SalarySlip(CoreMasterBase):
    """
    One per employee per month. Core transactional payroll record.
    0=Draft, 1=Submitted, 2=Cancelled
    """
    __tablename__ = "hr_salary_slips"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="RESTRICT"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False)
    salary_structure_id = Column(UUID(as_uuid=True), ForeignKey("hr_salary_structures.id", ondelete="RESTRICT"), nullable=True)
    payroll_month = Column(Integer, nullable=False)
    payroll_year = Column(Integer, nullable=False)
    working_days = Column(Integer, nullable=False)
    present_days = Column(Numeric(5, 2), nullable=False)
    lop_days = Column(Numeric(5, 2), default=0, nullable=False)

    # Earnings summary
    gross_earnings = Column(Numeric(12, 2), default=0, nullable=False)

    # Statutory deduction fields
    pf_employee = Column(Numeric(10, 2), default=0, nullable=False)
    pf_employer = Column(Numeric(10, 2), default=0, nullable=False)
    eps_employer = Column(Numeric(10, 2), default=0, nullable=False)
    esi_employee = Column(Numeric(10, 2), default=0, nullable=False)
    esi_employer = Column(Numeric(10, 2), default=0, nullable=False)
    professional_tax = Column(Numeric(10, 2), default=0, nullable=False)
    tds_amount = Column(Numeric(10, 2), default=0, nullable=False)

    # Totals
    total_deductions = Column(Numeric(12, 2), default=0, nullable=False)
    net_pay = Column(Numeric(12, 2), default=0, nullable=False)

    # State machine
    docstatus = Column(Integer, default=0, nullable=False)

    # Metadata
    posting_date = Column(Date, nullable=False)
    remarks = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "employee_id", "payroll_month", "payroll_year", name="uq_salary_slip_period"),
    )

    # Relationships
    employee = relationship("Employee")
    company = relationship("Company")
    salary_structure = relationship("SalaryStructure")
    earnings = relationship("SalarySlipEarning", back_populates="salary_slip", cascade="all, delete-orphan")
    deductions = relationship("SalarySlipDeduction", back_populates="salary_slip", cascade="all, delete-orphan")

class SalarySlipEarning(CoreMasterBase):
    """
    Child table — line-by-line earnings for one slip.
    """
    __tablename__ = "hr_salary_slip_earnings"

    salary_slip_id = Column(UUID(as_uuid=True), ForeignKey("hr_salary_slips.id", ondelete="CASCADE"), nullable=False)
    salary_component_id = Column(UUID(as_uuid=True), ForeignKey("hr_salary_components.id", ondelete="RESTRICT"), nullable=False)
    component_name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)

    # Relationships
    salary_slip = relationship("SalarySlip", back_populates="earnings")
    salary_component = relationship("SalaryComponent")

class SalarySlipDeduction(CoreMasterBase):
    """
    Child table — line-by-line deductions for one slip.
    """
    __tablename__ = "hr_salary_slip_deductions"

    salary_slip_id = Column(UUID(as_uuid=True), ForeignKey("hr_salary_slips.id", ondelete="CASCADE"), nullable=False)
    salary_component_id = Column(UUID(as_uuid=True), ForeignKey("hr_salary_components.id", ondelete="RESTRICT"), nullable=False)
    component_name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)

    # Relationships
    salary_slip = relationship("SalarySlip", back_populates="deductions")
    salary_component = relationship("SalaryComponent")
