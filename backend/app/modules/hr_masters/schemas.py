from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime

class HolidayBase(BaseModel):
    holiday_date: date
    description: str
    weekly_off: bool = False

class HolidayCreate(HolidayBase):
    pass

class HolidayUpdate(BaseModel):
    id: Optional[UUID] = None # For matching existing child records
    holiday_date: Optional[date] = None
    description: Optional[str] = None
    weekly_off: Optional[bool] = None

class HolidayResponse(HolidayBase):
    id: UUID
    holiday_list_id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HolidayListBase(BaseModel):
    holiday_list_name: str
    from_date: date
    to_date: date
    company: UUID
    weekly_off: str

class HolidayListCreate(HolidayListBase):
    holidays: List[HolidayCreate] = []

class HolidayListUpdate(BaseModel):
    holiday_list_name: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    company: Optional[UUID] = None
    weekly_off: Optional[str] = None
    holidays: Optional[List[HolidayUpdate]] = None

class HolidayListResponse(HolidayListBase):
    id: UUID
    tenant_id: UUID
    total_holidays: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    modified_by: Optional[UUID] = None
    holidays: List[HolidayResponse] = []

    model_config = ConfigDict(from_attributes=True)

# Employee Child Tables
class EmployeeEducationBase(BaseModel):
    school_univ: Optional[str] = None
    qualification: Optional[str] = None
    level: Optional[str] = None
    year_of_passing: Optional[int] = None
    class_per: Optional[str] = None
    maj_opt_subj: Optional[str] = None

class EmployeeEducationCreate(EmployeeEducationBase):
    pass

class EmployeeEducationUpdate(EmployeeEducationBase):
    id: Optional[UUID] = None

class EmployeeEducationResponse(EmployeeEducationBase):
    id: UUID
    employee_id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EmployeeExternalWorkHistoryBase(BaseModel):
    company_name: Optional[str] = None
    designation: Optional[str] = None
    salary: Optional[float] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    total_experience: Optional[str] = None

class EmployeeExternalWorkHistoryCreate(EmployeeExternalWorkHistoryBase):
    pass

class EmployeeExternalWorkHistoryUpdate(EmployeeExternalWorkHistoryBase):
    id: Optional[UUID] = None

class EmployeeExternalWorkHistoryResponse(EmployeeExternalWorkHistoryBase):
    id: UUID
    employee_id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EmployeeInternalWorkHistoryBase(BaseModel):
    branch_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None

class EmployeeInternalWorkHistoryCreate(EmployeeInternalWorkHistoryBase):
    pass

class EmployeeInternalWorkHistoryUpdate(EmployeeInternalWorkHistoryBase):
    id: Optional[UUID] = None

class EmployeeInternalWorkHistoryResponse(EmployeeInternalWorkHistoryBase):
    id: UUID
    employee_id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Employee Master
class EmployeeBase(BaseModel):
    naming_series: str = "HR-EMP-"
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    salutation_id: Optional[UUID] = None
    gender_id: UUID
    date_of_birth: date
    image: Optional[str] = None
    employee_number: Optional[str] = None
    status: str = "Active"
    user_id: Optional[UUID] = None
    company_id: UUID
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    reports_to_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    employment_type_id: Optional[UUID] = None
    employee_grade_id: Optional[UUID] = None
    date_of_joining: date
    scheduled_confirmation_date: Optional[date] = None
    final_confirmation_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    notice_number_of_days: Optional[int] = None
    date_of_retirement: Optional[date] = None
    attendance_device_id: Optional[str] = None
    holiday_list_id: Optional[UUID] = None
    salary_mode: Optional[str] = None
    salary_currency_id: Optional[UUID] = None
    ctc: Optional[float] = None
    bank_name: Optional[str] = None
    bank_ac_no: Optional[str] = None
    iban: Optional[str] = None
    cell_number: Optional[str] = None
    company_email: Optional[str] = None
    personal_email: Optional[str] = None
    prefered_contact_email: Optional[str] = None
    current_address: Optional[str] = None
    current_accommodation_type: Optional[str] = None
    permanent_address: Optional[str] = None
    permanent_accommodation_type: Optional[str] = None
    person_to_be_contacted: Optional[str] = None
    emergency_phone_number: Optional[str] = None
    relation: Optional[str] = None
    marital_status: Optional[str] = None
    blood_group: Optional[str] = None
    family_background: Optional[str] = None
    health_details: Optional[str] = None
    passport_number: Optional[str] = None
    passport_date_of_issue: Optional[date] = None
    passport_valid_upto: Optional[date] = None
    passport_place_of_issue: Optional[str] = None
    bio: Optional[str] = None
    resignation_letter_date: Optional[date] = None
    relieving_date: Optional[date] = None
    reason_for_leaving: Optional[str] = None
    leave_encashed: Optional[str] = None
    encashment_date: Optional[date] = None

class EmployeeCreate(EmployeeBase):
    education: List[EmployeeEducationCreate] = []
    external_work_history: List[EmployeeExternalWorkHistoryCreate] = []
    internal_work_history: List[EmployeeInternalWorkHistoryCreate] = []

class EmployeeUpdate(BaseModel):
    # Only a subset for brevity in the update schema
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[str] = None
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    reports_to_id: Optional[UUID] = None
    education: Optional[List[EmployeeEducationUpdate]] = None
    external_work_history: Optional[List[EmployeeExternalWorkHistoryUpdate]] = None
    internal_work_history: Optional[List[EmployeeInternalWorkHistoryUpdate]] = None

class EmployeeResponse(EmployeeBase):
    id: UUID
    tenant_id: UUID
    employee_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    education: List[EmployeeEducationResponse] = []
    external_work_history: List[EmployeeExternalWorkHistoryResponse] = []
    internal_work_history: List[EmployeeInternalWorkHistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)

# --- Leave Management Schemas ---

class LeaveTypeBase(BaseModel):
    leave_type_name: str
    max_leaves_allowed: Optional[float] = None
    applicable_after: Optional[int] = None
    max_continuous_days_allowed: Optional[int] = None
    
    is_carry_forward: bool = False
    maximum_carry_forwarded_leaves: Optional[float] = None
    expire_carry_forwarded_leaves_after_days: Optional[int] = None
    
    is_lwp: bool = False
    is_ppl: bool = False
    fraction_of_daily_salary_per_leave: Optional[float] = None
    
    is_optional_leave: bool = False
    allow_negative: bool = False
    allow_over_allocation: bool = False
    include_holiday: bool = False
    is_compensatory: bool = False
    
    allow_encashment: bool = False
    max_encashable_leaves: Optional[int] = None
    non_encashable_leaves: Optional[int] = None
    
    is_earned_leave: bool = False
    earned_leave_frequency: Optional[str] = None
    allocate_on_day: str = "Last Day"
    rounding: Optional[str] = None

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeUpdate(BaseModel):
    leave_type_name: Optional[str] = None
    max_leaves_allowed: Optional[float] = None
    is_carry_forward: Optional[bool] = None
    is_lwp: Optional[bool] = None
    is_earned_leave: Optional[bool] = None

class LeaveTypeResponse(LeaveTypeBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LeaveApplicationBase(BaseModel):
    employee_id: UUID
    leave_type_id: UUID
    company_id: UUID
    leave_approver_id: Optional[UUID] = None
    amended_from_id: Optional[UUID] = None
    
    from_date: date
    to_date: date
    posting_date: date
    
    half_day: bool = False
    half_day_date: Optional[date] = None
    
    total_leave_days: Optional[float] = None
    leave_balance: Optional[float] = None
    
    description: Optional[str] = None
    follow_via_email: bool = True
    color: Optional[str] = None

class LeaveApplicationCreate(LeaveApplicationBase):
    naming_series: str = "HR-LAP-.YYYY.-."
    docstatus: int = 0
    status: str = "Open"

class LeaveApplicationUpdate(BaseModel):
    leave_approver_id: Optional[UUID] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    half_day: Optional[bool] = None
    description: Optional[str] = None

class LeaveApplicationResponse(LeaveApplicationBase):
    id: UUID
    tenant_id: UUID
    naming_series: str
    docstatus: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Eagerly loaded nested details for the UI. Optional to avoid serialization errors if missing.
    employee: Optional[EmployeeResponse] = None
    leave_type: Optional[LeaveTypeResponse] = None
    
    model_config = ConfigDict(from_attributes=True)
