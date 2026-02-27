from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class DepartmentBase(BaseModel):
    department_name: str
    parent_department: Optional[UUID] = None
    company: UUID
    is_group: bool = False
    disabled: bool = False

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = None
    parent_department: Optional[UUID] = None
    company: Optional[UUID] = None
    is_group: Optional[bool] = None
    disabled: Optional[bool] = None

class DepartmentResponse(DepartmentBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    modified_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

class EmployeeGradeBase(BaseModel):
    grade_name: str
    default_base_pay: Optional[float] = None
    currency_id: Optional[UUID] = None

class EmployeeGradeCreate(EmployeeGradeBase):
    pass

class EmployeeGradeUpdate(BaseModel):
    grade_name: Optional[str] = None
    default_base_pay: Optional[float] = None
    currency_id: Optional[UUID] = None

class EmployeeGradeResponse(EmployeeGradeBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

