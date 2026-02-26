Module Name: Leave Type
Module: HRMS / HR
Type: Master
DocStatus: No

Description
Defines a category of leave (e.g., Annual Leave, Sick Leave, Maternity). Controls rules for carry-forward, encashment, earned-leave accrual, and LWP behavior.

Dependencies
- Salary Component (Payroll, for encashment earning component)

Schema Fields
leave_type_name: Data, Mandatory, Unique.
max_leaves_allowed: Float, Optional.
applicable_after: Int, Optional (working days required since joining before applying).
max_continuous_days_allowed: Int, Optional.
is_carry_forward: Check, Default: 0.
maximum_carry_forwarded_leaves: Float, Optional (shown if is_carry_forward = 1).
expire_carry_forwarded_leaves_after_days: Int, Optional (shown if is_carry_forward = 1).
is_lwp: Check, Default: 0 (Is Leave Without Pay).
is_ppl: Check, Default: 0 (Is Partially Paid Leave).
fraction_of_daily_salary_per_leave: Float, Mandatory if is_ppl = 1.
is_optional_leave: Check, Default: 0.
allow_negative: Check, Default: 0.
allow_over_allocation: Check, Default: 0.
include_holiday: Check, Default: 0.
is_compensatory: Check, Default: 0.
allow_encashment: Check, Default: 0.
max_encashable_leaves: Int, Optional (shown if allow_encashment = 1).
non_encashable_leaves: Int, Optional (shown if allow_encashment = 1).
earning_component: Link → Salary Component, Optional (shown if allow_encashment = 1).
is_earned_leave: Check, Default: 0.
earned_leave_frequency: Select (Monthly, Quarterly, Half-Yearly, Yearly), Optional (shown if is_earned_leave = 1).
allocate_on_day: Select (First Day, Last Day, Date of Joining), Default: Last Day (shown if is_earned_leave = 1).
rounding: Select (0.25, 0.5, 1.0), Optional (shown if is_earned_leave = 1).
