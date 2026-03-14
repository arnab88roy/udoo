from sqlalchemy import Column, String, Boolean, Date, ForeignKey, Integer, Numeric, Text, CheckConstraint, DateTime, UniqueConstraint
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from app.modules.core_masters.models import CoreMasterBase

class HolidayList(CoreMasterBase):
    __tablename__ = "hr_holiday_lists"

    holiday_list_name = Column(String, nullable=False, unique=True, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    company = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="CASCADE"), nullable=False, index=True)
    weekly_off = Column(String, nullable=False)
    total_holidays = Column(Integer, default=0, nullable=False)

    # Relationship to its child table
    holidays = relationship("Holiday", back_populates="holiday_list", cascade="all, delete-orphan")

class Holiday(CoreMasterBase):
    __tablename__ = "hr_holidays"

    holiday_list_id = Column(UUID(as_uuid=True), ForeignKey("hr_holiday_lists.id", ondelete="CASCADE"), nullable=False, index=True)
    holiday_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    weekly_off = Column(Boolean, default=False, nullable=False)

    # Relationship to parent
    holiday_list = relationship("HolidayList", back_populates="holidays")

class Employee(CoreMasterBase):
    __tablename__ = "hr_employees"

    # Basic Info
    naming_series = Column(String, default="HR-EMP-")
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    employee_name = Column(String, nullable=True) # Computed Full Name
    salutation_id = Column(UUID(as_uuid=True), ForeignKey("hr_salutations.id", ondelete="SET NULL"), nullable=True)
    gender_id = Column(UUID(as_uuid=True), ForeignKey("hr_genders.id", ondelete="RESTRICT"), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    image = Column(Text, nullable=True)
    employee_number = Column(String, nullable=True)

    # Status
    status = Column(String, nullable=False, default="Active")
    user_id = Column(UUID(as_uuid=True), ForeignKey("hr_users.id", ondelete="SET NULL"), nullable=True)

    # Company Details
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("hr_departments.id", ondelete="SET NULL"), nullable=True)
    designation_id = Column(UUID(as_uuid=True), ForeignKey("hr_designations.id", ondelete="SET NULL"), nullable=True)
    reports_to_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="SET NULL"), nullable=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("hr_branches.id", ondelete="SET NULL"), nullable=True)
    employment_type_id = Column(UUID(as_uuid=True), ForeignKey("hr_employment_types.id", ondelete="SET NULL"), nullable=True)
    employee_grade_id = Column(UUID(as_uuid=True), ForeignKey("hr_employee_grades.id", ondelete="SET NULL"), nullable=True)

    # Joining & Contract
    date_of_joining = Column(Date, nullable=False)
    scheduled_confirmation_date = Column(Date, nullable=True)
    final_confirmation_date = Column(Date, nullable=True)
    contract_end_date = Column(Date, nullable=True)
    notice_number_of_days = Column(Integer, nullable=True)
    date_of_retirement = Column(Date, nullable=True)

    # Attendance & Leave
    attendance_device_id = Column(String, unique=True, nullable=True)
    holiday_list_id = Column(UUID(as_uuid=True), ForeignKey("hr_holiday_lists.id", ondelete="SET NULL"), nullable=True)

    # Salary Structure Mapping
    salary_structure_id = Column(UUID(as_uuid=True), ForeignKey("hr_salary_structures.id", ondelete="SET NULL"), nullable=True)

    # Salary
    salary_mode = Column(String, nullable=True)
    salary_currency_id = Column(UUID(as_uuid=True), ForeignKey("hr_currencies.id", ondelete="SET NULL"), nullable=True)
    ctc = Column(Numeric(18, 2), nullable=True)
    bank_name = Column(String, nullable=True)
    bank_ac_no = Column(String, nullable=True)
    iban = Column(String, nullable=True)

    # Contact
    cell_number = Column(String, nullable=True)
    company_email = Column(String, nullable=True)
    personal_email = Column(String, nullable=True)
    prefered_contact_email = Column(String, nullable=True)
    prefered_email = Column(String, nullable=True)
    unsubscribed = Column(Boolean, default=False)

    # Address
    current_address = Column(Text, nullable=True)
    current_accommodation_type = Column(String, nullable=True)
    permanent_address = Column(Text, nullable=True)
    permanent_accommodation_type = Column(String, nullable=True)

    # Emergency Contact
    person_to_be_contacted = Column(String, nullable=True)
    emergency_phone_number = Column(String, nullable=True)
    relation = Column(String, nullable=True)

    # Personal Details
    marital_status = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    family_background = Column(Text, nullable=True)
    health_details = Column(Text, nullable=True)
    passport_number = Column(String, nullable=True)
    passport_date_of_issue = Column(Date, nullable=True)
    passport_valid_upto = Column(Date, nullable=True)
    passport_place_of_issue = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    # Exit Info
    resignation_letter_date = Column(Date, nullable=True)
    relieving_date = Column(Date, nullable=True)
    reason_for_leaving = Column(Text, nullable=True)
    leave_encashed = Column(String, nullable=True)
    encashment_date = Column(Date, nullable=True)

    # Relationships
    education = relationship("EmployeeEducation", back_populates="employee", cascade="all, delete-orphan")
    external_work_history = relationship("EmployeeExternalWorkHistory", back_populates="employee", cascade="all, delete-orphan")
    internal_work_history = relationship("EmployeeInternalWorkHistory", back_populates="employee", cascade="all, delete-orphan")

class EmployeeEducation(CoreMasterBase):
    __tablename__ = "hr_employee_educations"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    school_univ = Column(Text, nullable=True)
    qualification = Column(String, nullable=True)
    level = Column(String, nullable=True)
    year_of_passing = Column(Integer, nullable=True)
    class_per = Column(String, nullable=True)
    maj_opt_subj = Column(Text, nullable=True)

    employee = relationship("Employee", back_populates="education")

class EmployeeExternalWorkHistory(CoreMasterBase):
    __tablename__ = "hr_employee_external_work_history"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    salary = Column(Numeric(18, 2), nullable=True)
    address = Column(Text, nullable=True)
    contact = Column(String, nullable=True)
    total_experience = Column(String, nullable=True)

    employee = relationship("Employee", back_populates="external_work_history")

class EmployeeInternalWorkHistory(CoreMasterBase):
    __tablename__ = "hr_employee_internal_work_history"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("hr_branches.id", ondelete="SET NULL"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("hr_departments.id", ondelete="SET NULL"), nullable=True)
    designation_id = Column(UUID(as_uuid=True), ForeignKey("hr_designations.id", ondelete="SET NULL"), nullable=True)
    from_date = Column(Date, nullable=True)
    to_date = Column(Date, nullable=True)

    employee = relationship("Employee", back_populates="internal_work_history")

# --- Leave Management ---

class LeaveType(CoreMasterBase):
    __tablename__ = "hr_leave_types"

    leave_type_name = Column(String, nullable=False, unique=True, index=True)
    max_leaves_allowed = Column(Numeric(18, 2), nullable=True)
    applicable_after = Column(Integer, nullable=True)
    max_continuous_days_allowed = Column(Integer, nullable=True)
    
    is_carry_forward = Column(Boolean, default=False, nullable=False)
    maximum_carry_forwarded_leaves = Column(Numeric(18, 2), nullable=True)
    expire_carry_forwarded_leaves_after_days = Column(Integer, nullable=True)
    
    is_lwp = Column(Boolean, default=False, nullable=False)
    is_ppl = Column(Boolean, default=False, nullable=False)
    fraction_of_daily_salary_per_leave = Column(Numeric(18, 2), nullable=True)
    
    is_optional_leave = Column(Boolean, default=False, nullable=False)
    allow_negative = Column(Boolean, default=False, nullable=False)
    allow_over_allocation = Column(Boolean, default=False, nullable=False)
    include_holiday = Column(Boolean, default=False, nullable=False)
    is_compensatory = Column(Boolean, default=False, nullable=False)
    
    allow_encashment = Column(Boolean, default=False, nullable=False)
    max_encashable_leaves = Column(Integer, nullable=True)
    non_encashable_leaves = Column(Integer, nullable=True)
    
    is_earned_leave = Column(Boolean, default=False, nullable=False)
    earned_leave_frequency = Column(String, nullable=True)
    allocate_on_day = Column(String, default="Last Day", nullable=True)
    rounding = Column(String, nullable=True)


class LeaveApplication(CoreMasterBase):
    __tablename__ = "hr_leave_applications"

    # Transaction State
    docstatus = Column(Integer, default=0, nullable=False)
    status = Column(String, default="Open", nullable=False)
    
    naming_series = Column(String, default="HR-LAP-.YYYY.-.", nullable=False)
    
    # Foreign Keys
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="RESTRICT"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("hr_leave_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    leave_approver_id = Column(UUID(as_uuid=True), ForeignKey("hr_users.id", ondelete="SET NULL"), nullable=True, index=True)
    amended_from_id = Column(UUID(as_uuid=True), ForeignKey("hr_leave_applications.id", ondelete="SET NULL"), nullable=True)
    
    # Dates
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    posting_date = Column(Date, nullable=False)
    
    # Half Day
    half_day = Column(Boolean, default=False, nullable=False)
    half_day_date = Column(Date, nullable=True)
    
    # Quantities
    total_leave_days = Column(Numeric(18, 2), nullable=True)
    leave_balance = Column(Numeric(18, 2), nullable=True)
    
    # Text
    description = Column(Text, nullable=True)
    follow_via_email = Column(Boolean, default=True, nullable=False)
    color = Column(String, nullable=True)

    # Relationships
    employee = relationship("Employee")
    leave_type = relationship("LeaveType")
    # leave_approver mapped to User (which is in core_masters.models) is technically doable but leaving it simple for eager load
    # company mapped to Company
    # amended_from mapped to LeaveApplication

# --- Attendance Management ---

class EmployeeCheckin(CoreMasterBase):
    __tablename__ = "hr_employee_checkins"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="RESTRICT"), nullable=False, index=True)
    log_type = Column(String, nullable=False) # "IN" or "OUT"
    time = Column(DateTime(timezone=True), nullable=False)
    device_id = Column(String, nullable=True)
    skip_auto_attendance = Column(Boolean, default=False, nullable=False)

    # Relationships
    employee = relationship("Employee")

class Attendance(CoreMasterBase):
    __tablename__ = "hr_attendance"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="RESTRICT"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False)
    status = Column(String, nullable=False) # "Present", "Absent", etc.
    docstatus = Column(Integer, default=0, nullable=False)
    working_hours = Column(Numeric(5, 2), nullable=True)
    late_entry = Column(Boolean, default=False, nullable=False)
    early_exit = Column(Boolean, default=False, nullable=False)
    leave_application_id = Column(UUID(as_uuid=True), ForeignKey("hr_leave_applications.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        UniqueConstraint('employee_id', 'attendance_date', name='uq_employee_attendance_date'),
    )

    # Relationships
    employee = relationship("Employee")
    leave_application = relationship("LeaveApplication")

class AttendanceRequest(CoreMasterBase):
    __tablename__ = "hr_attendance_requests"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("hr_employees.id", ondelete="RESTRICT"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    docstatus = Column(Integer, default=0, nullable=False)
    status = Column(String, default="Open", nullable=False)

    # Relationships
    employee = relationship("Employee")
