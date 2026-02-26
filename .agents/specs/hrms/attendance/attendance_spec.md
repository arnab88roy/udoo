Module Name: Attendance
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Records the daily attendance status of an employee (Present, Absent, On Leave, Half Day, Work From Home). Auto-created by the shift/checkin processor or submitted manually.

Dependencies
- Employee
- Company
- Department
- Leave Type (leave/)
- Leave Application (leave/)
- Attendance Request (attendance/)
- Shift Type (shift/)
- Overtime Type (overtime/)

Schema Fields
naming_series: Select, Mandatory, Default: HR-ATT-.YYYY.-.
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
attendance_date: Date, Mandatory.
status: Select (Present, Absent, On Leave, Half Day, Work From Home), Mandatory, Default: Present.
working_hours: Float, Read Only.
leave_type: Link → Leave Type, Mandatory if status = On Leave or Half Day.
leave_application: Link → Leave Application, Read Only.
company: Link → Company, Mandatory, Read Only (fetched from employee).
department: Link → Department, Read Only (fetched from employee).
shift: Link → Shift Type, Optional.
attendance_request: Link → Attendance Request, Read Only.
late_entry: Check, Default: 0.
early_exit: Check, Default: 0.
in_time: Datetime, Read Only (shown if shift is set).
out_time: Datetime, Read Only (shown if shift is set).
half_day_status: Select (Present, Absent), Optional (status for the other half on a half-day record).
overtime_type: Link → Overtime Type, Read Only.
standard_working_hours: Float, Read Only.
actual_overtime_duration: Float, Read Only.
amended_from: Link → Attendance, Read Only.
