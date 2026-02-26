Module Name: Shift Type
Module: HRMS / HR
Type: Master
DocStatus: No

Description
Defines a named work shift with its start/end times, auto-attendance rules, late entry/early exit grace periods, and overtime configuration.

Dependencies
- Holiday List (core_masters)
- Overtime Type (overtime/)

Schema Fields
name: Data, Mandatory (set by user — the shift name, e.g. "Morning", "Night").
start_time: Time, Mandatory.
end_time: Time, Mandatory.
holiday_list: Link → Holiday List, Optional.
color: Select (Blue, Cyan, Fuchsia, Green, Lime, Orange, Pink, Red, Violet, Yellow), Default: Blue.
enable_auto_attendance: Check, Default: 0.
determine_check_in_and_check_out: Select (Alternating entries as IN and OUT during the same shift, Strictly based on Log Type in Employee Checkin), Optional.
working_hours_calculation_based_on: Select (First Check-in and Last Check-out, Every Valid Check-in and Check-out), Optional.
begin_check_in_before_shift_start_time: Int, Default: 60 (minutes).
allow_check_out_after_shift_end_time: Int, Default: 60 (minutes).
mark_auto_attendance_on_holidays: Check, Default: 0.
working_hours_threshold_for_half_day: Float, Optional.
working_hours_threshold_for_absent: Float, Optional.
process_attendance_after: Date, Mandatory if enable_auto_attendance = 1.
last_sync_of_checkin: Datetime, Optional.
auto_update_last_sync: Check, Default: 0.
enable_late_entry_marking: Check, Default: 0.
late_entry_grace_period: Int, Optional (shown if enable_late_entry_marking = 1).
enable_early_exit_marking: Check, Default: 0.
early_exit_grace_period: Int, Optional (shown if enable_early_exit_marking = 1).
allow_overtime: Check, Default: 0.
overtime_type: Link → Overtime Type, Mandatory if allow_overtime = 1.
