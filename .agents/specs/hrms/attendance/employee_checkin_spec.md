Module Name: Employee Checkin
Module: HRMS / HR
Type: Log Record
DocStatus: No

Description
Records raw biometric or manual IN/OUT timestamps for an employee. Used by the automated attendance processor to generate Attendance records for each shift.

Dependencies
- Employee
- Shift Type (shift/)
- Attendance (attendance/)
- Overtime Type (overtime/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only (fetched from employee).
log_type: Select (IN, OUT), Optional.
time: Datetime, Mandatory, Default: Now.
shift: Link → Shift Type, Read Only.
device_id: Data, Optional (Location / Device ID).
skip_auto_attendance: Check, Default: 0.
attendance: Link → Attendance, Read Only (populated after attendance is marked).
latitude: Float, Read Only.
longitude: Float, Read Only.
geolocation: Geolocation, Read Only.
overtime_type: Link → Overtime Type, Hidden, Read Only.
shift_start: Datetime, Hidden.
shift_end: Datetime, Hidden.
shift_actual_start: Datetime, Hidden.
shift_actual_end: Datetime, Hidden.
offshift: Check, Hidden, Read Only.
