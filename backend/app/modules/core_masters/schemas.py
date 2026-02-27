from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class CoreMasterSchemaBase(BaseModel):
    """Abstract base schema for all standard Meta-Engine tables."""
    pass

class CoreMasterSchemaResponse(CoreMasterSchemaBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    modified_by: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)

# ====== Company ======
class CompanyBase(CoreMasterSchemaBase):
    company_name: str
    abbr: str
    domain: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    abbr: Optional[str] = None
    domain: Optional[str] = None

class CompanyResponse(CompanyBase, CoreMasterSchemaResponse):
    pass

# ====== Branch ======
class BranchBase(CoreMasterSchemaBase):
    branch: str

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    branch: Optional[str] = None

class BranchResponse(BranchBase, CoreMasterSchemaResponse):
    pass

# ====== Gender ======
class GenderBase(CoreMasterSchemaBase):
    name: str

class GenderCreate(GenderBase):
    pass

class GenderUpdate(BaseModel):
    name: Optional[str] = None

class GenderResponse(GenderBase, CoreMasterSchemaResponse):
    pass

# ====== Salutation ======
class SalutationBase(CoreMasterSchemaBase):
    name: str

class SalutationCreate(SalutationBase):
    pass

class SalutationUpdate(BaseModel):
    name: Optional[str] = None

class SalutationResponse(SalutationBase, CoreMasterSchemaResponse):
    pass

# ====== EmploymentType ======
class EmploymentTypeBase(CoreMasterSchemaBase):
    employee_type_name: str

class EmploymentTypeCreate(EmploymentTypeBase):
    pass

class EmploymentTypeUpdate(BaseModel):
    employee_type_name: Optional[str] = None

class EmploymentTypeResponse(EmploymentTypeBase, CoreMasterSchemaResponse):
    pass

# ====== Designation ======
class DesignationBase(CoreMasterSchemaBase):
    designation_name: str
    description: Optional[str] = None

class DesignationCreate(DesignationBase):
    pass

class DesignationUpdate(BaseModel):
    designation_name: Optional[str] = None
    description: Optional[str] = None

class DesignationResponse(DesignationBase, CoreMasterSchemaResponse):
    pass

# ====== Skill ======
class SkillBase(CoreMasterSchemaBase):
    skill_name: str
    description: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    skill_name: Optional[str] = None
    description: Optional[str] = None

class SkillResponse(SkillBase, CoreMasterSchemaResponse):
    pass

# ====== Currency ======
class CurrencyBase(CoreMasterSchemaBase):
    currency_code: str
    currency_symbol: Optional[str] = None
    fraction: Optional[str] = None
    fraction_units: Optional[int] = 100

class CurrencyCreate(CurrencyBase):
    pass

class CurrencyUpdate(BaseModel):
    currency_code: Optional[str] = None
    currency_symbol: Optional[str] = None
    fraction: Optional[str] = None
    fraction_units: Optional[int] = None

class CurrencyResponse(CurrencyBase, CoreMasterSchemaResponse):
    pass

# ====== User ======
class UserBase(CoreMasterSchemaBase):
    email: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase, CoreMasterSchemaResponse):
    pass

