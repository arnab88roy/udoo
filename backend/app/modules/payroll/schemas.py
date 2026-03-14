from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date, datetime

# --- Compliance Settings ---

class ComplianceSettingsBase(BaseModel):
    company_id: UUID = Field(..., description="ID of the company these settings apply to. Unique per company.")
    pf_applicable: bool = Field(False, description="True if company has 20+ employees and PF is mandatory.")
    esi_applicable: bool = Field(False, description="True if company has 10+ employees and ESI is mandatory.")
    pt_applicable: bool = Field(False, description="Professional Tax applicability — depends on branch state.")
    tds_applicable: bool = Field(True, description="TDS under Section 192 — always applicable for salaried employees.")
    pf_wage_ceiling: float = Field(15000.00, description="PF contribution capped on this basic wage amount. Default ₹15,000 per EPFO rules.")
    esi_gross_ceiling: float = Field(21000.00, description="ESI applicable only if employee gross salary is below this amount. Default ₹21,000.")

class ComplianceSettingsCreate(ComplianceSettingsBase):
    pass

class ComplianceSettingsUpdate(BaseModel):
    pf_applicable: Optional[bool] = None
    esi_applicable: Optional[bool] = None
    pt_applicable: Optional[bool] = None
    tds_applicable: Optional[bool] = None
    pf_wage_ceiling: Optional[float] = None
    esi_gross_ceiling: Optional[float] = None

class ComplianceSettingsResponse(ComplianceSettingsBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Professional Tax Slab ---

class ProfessionalTaxSlabBase(BaseModel):
    state_code: str = Field(..., description="Two-letter Indian state code. E.g. MH=Maharashtra, KA=Karnataka, GJ=Gujarat.")
    min_salary: float = Field(..., description="Minimum monthly gross salary for this slab (inclusive).")
    max_salary: Optional[float] = Field(None, description="Maximum monthly gross salary for this slab (inclusive). NULL means no upper limit.")
    pt_amount: float = Field(..., description="Fixed PT amount to deduct for this slab in rupees.")
    is_february: bool = Field(False, description="If True, this slab applies only in February. Some states charge different PT in Feb.")
    effective_from: date = Field(..., description="Date from which this slab is effective.")

class ProfessionalTaxSlabCreate(ProfessionalTaxSlabBase):
    pass

class ProfessionalTaxSlabResponse(ProfessionalTaxSlabBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Salary Component ---

class SalaryComponentBase(BaseModel):
    component_name: str = Field(..., description="Display name of the component. E.g. Basic, HRA, PF Employee Contribution.")
    component_type: Literal["Earning", "Deduction", "Employer Contribution", "Informational"] = Field(..., description="Type of component.")
    is_statutory: bool = Field(False, description="True for government-mandated components: PF, ESI, PT, TDS.")
    is_taxable: bool = Field(True, description="True if this component is included in taxable income calculation.")
    is_active: bool = Field(True, description="True if the component is active for use.")
    description: Optional[str] = Field(None, description="Description of the component for VEDA AI context.")

class SalaryComponentCreate(SalaryComponentBase):
    pass

class SalaryComponentUpdate(BaseModel):
    component_name: Optional[str] = None
    component_type: Optional[Literal["Earning", "Deduction", "Employer Contribution", "Informational"]] = None
    is_statutory: Optional[bool] = None
    is_taxable: Optional[bool] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None

class SalaryComponentResponse(SalaryComponentBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Salary Structure Component ---

class SalaryStructureComponentBase(BaseModel):
    salary_component_id: UUID = Field(..., description="ID of the salary component.")
    calculation_type: Literal["Fixed", "Percentage of Basic", "Percentage of Gross", "Statutory"] = Field(..., description="How this component amount is calculated.")
    value: float = Field(..., description="The fixed amount OR the percentage value. E.g. 50.0 means 50%.")
    order_index: int = Field(0, description="Display order of components in the salary slip.")

class SalaryStructureComponentCreate(SalaryStructureComponentBase):
    pass

class SalaryStructureComponentUpdate(BaseModel):
    id: Optional[UUID] = None  # To match existing records
    salary_component_id: Optional[UUID] = None
    calculation_type: Optional[Literal["Fixed", "Percentage of Basic", "Percentage of Gross", "Statutory"]] = None
    value: Optional[float] = None
    order_index: Optional[int] = None

class SalaryStructureComponentResponse(SalaryStructureComponentBase):
    id: UUID
    tenant_id: UUID
    salary_structure_id: UUID
    salary_component: Optional[SalaryComponentResponse] = None

    model_config = ConfigDict(from_attributes=True)

# --- Salary Structure ---

class SalaryStructureBase(BaseModel):
    structure_name: str = Field(..., description="Name of the salary structure. E.g. Junior Engineer Structure, Sales Executive Structure.")
    company_id: UUID = Field(..., description="ID of the company this structure belongs to.")
    is_active: bool = Field(True, description="True if the structure is active.")
    description: Optional[str] = Field(None, description="Description of the structure for VEDA AI context.")

class SalaryStructureCreate(SalaryStructureBase):
    components: List[SalaryStructureComponentCreate] = Field([], description="List of components linking to this structure.")

class SalaryStructureUpdate(BaseModel):
    structure_name: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None

class SalaryStructureResponse(SalaryStructureBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    components: List[SalaryStructureComponentResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Salary Slip Earnings / Deductions ---

class SalarySlipEarningBase(BaseModel):
    salary_component_id: UUID = Field(..., description="ID of the salary component.")
    component_name: str = Field(..., description="Snapshot of component name.")
    amount: float = Field(..., description="Earning amount for this component.")

class SalarySlipEarningResponse(SalarySlipEarningBase):
    id: UUID
    tenant_id: UUID
    salary_slip_id: UUID

    model_config = ConfigDict(from_attributes=True)

class SalarySlipDeductionBase(BaseModel):
    salary_component_id: UUID = Field(..., description="ID of the salary component.")
    component_name: str = Field(..., description="Snapshot of component name.")
    amount: float = Field(..., description="Deduction amount for this component.")

class SalarySlipDeductionResponse(SalarySlipDeductionBase):
    id: UUID
    tenant_id: UUID
    salary_slip_id: UUID

    model_config = ConfigDict(from_attributes=True)

# --- Salary Slip ---

class SalarySlipBase(BaseModel):
    employee_id: UUID = Field(..., description="ID of the employee.")
    company_id: UUID = Field(..., description="ID of the company.")
    salary_structure_id: Optional[UUID] = Field(None, description="ID of the salary structure used.")
    payroll_month: int = Field(..., ge=1, le=12, description="Month number 1-12.")
    payroll_year: int = Field(..., description="Financial year e.g. 2026.")
    working_days: int = Field(..., description="Total working days in the month.")
    present_days: float = Field(..., description="Actual days present.")
    lop_days: float = Field(0, description="Loss of Pay days.")
    gross_earnings: float = Field(0, description="Total electronics.")
    pf_employee: float = Field(0, description="Employee PF contribution.")
    pf_employer: float = Field(0, description="Employer PF contribution.")
    eps_employer: float = Field(0, description="Employer EPS contribution.")
    esi_employee: float = Field(0, description="Employee ESI contribution.")
    esi_employer: float = Field(0, description="Employer ESI contribution.")
    professional_tax: float = Field(0, description="Professional Tax deduction.")
    tds_amount: float = Field(0, description="TDS deduction.")
    total_deductions: float = Field(0, description="Sum of all deductions.")
    net_pay: float = Field(0, description="gross_earnings minus total_deductions.")
    docstatus: int = Field(0, description="0=Draft, 1=Submitted/Processed, 2=Cancelled.")
    posting_date: date = Field(..., description="Date on which this salary slip was generated.")
    remarks: Optional[str] = Field(None, description="Optional HR notes.")

class SalarySlipCreate(SalarySlipBase):
    earnings: List[SalarySlipEarningBase] = []
    deductions: List[SalarySlipDeductionBase] = []

class SalarySlipResponse(SalarySlipBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    earnings: List[SalarySlipEarningResponse] = []
    deductions: List[SalarySlipDeductionResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Requests ---

class BulkGenerateRequest(BaseModel):
    company_id: UUID = Field(..., description="Company for which to generate slips.")
    payroll_month: int = Field(..., ge=1, le=12, description="Month number 1-12.")
    payroll_year: int = Field(..., description="Year e.g. 2026.")
    working_days: int = Field(..., description="Total working days in this month for this company.")
