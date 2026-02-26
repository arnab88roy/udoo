Module Name: Leave Encashment
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Records the monetization of unused leave days. On submission, calculates the encashment amount and triggers payroll or payment entry processing.

Dependencies
- Employee
- Company
- Department
- Currency
- Leave Type (leave/)
- Leave Period (leave/)
- Leave Allocation (leave/)
- Salary Component / Additional Salary (Payroll)
- Account (Finance, for expense and payable accounts)
- Cost Center (Finance)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only (fetched from employee).
company: Link → Company, Mandatory (fetched from employee).
leave_period: Link → Leave Period, Mandatory.
leave_type: Link → Leave Type, Mandatory.
leave_allocation: Link → Leave Allocation, Read Only.
leave_balance: Float, Read Only.
actual_encashable_days: Float, Read Only.
encashment_days: Float, Optional.
encashment_amount: Currency, Read Only.
currency: Link → Currency, Mandatory, Read Only.
encashment_date: Date, Default: Today.
additional_salary: Link → Additional Salary, Read Only.
pay_via_payment_entry: Check, Default: 0.
posting_date: Date, Optional (shown if pay_via_payment_entry = 1).
expense_account: Link → Account, Mandatory if pay_via_payment_entry = 1.
payable_account: Link → Account, Mandatory if pay_via_payment_entry = 1.
paid_amount: Currency, Read Only.
cost_center: Link → Cost Center, Optional.
status: Select (Draft, Unpaid, Paid, Submitted, Cancelled), Read Only.
amended_from: Link → Leave Encashment, Read Only.
