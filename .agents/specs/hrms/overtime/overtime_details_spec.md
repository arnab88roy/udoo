Module Name: Overtime Details
Module: HRMS / HR
Type: Child Table (of Overtime Slip)
DocStatus: No

Description
A single date-wise row of overtime hours worked, linked back to the specific Attendance record.

Parent
Overtime Slip (field: overtime_details)

Dependencies
- Attendance (attendance/)

Schema Fields
attendance_date: Date, Mandatory.
attendance: Link → Attendance, Optional.
overtime_hours: Float, Mandatory.
