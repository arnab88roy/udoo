Module Name: Expense Claim
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
An employee request for reimbursement of out-of-pocket business expenses. On submission, creates accounting entries. Supports approval workflow and advance deduction.

Dependencies
- Employee
- Company
- Department
- Expense Claim Type (expense/)
- Employee Advance (lifecycle/)
- Account (Finance)
- Cost Center (Finance)
- Currency

Schema Fields
naming_series: Select, Mandatory.
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only.
company: Link → Company, Mandatory.
posting_date: Date, Mandatory, Default: Today.
approval_status: Select (Draft, Approved, Rejected), Mandatory, Default: Draft.
total_claimed_amount: Currency, Read Only.
total_sanctioned_amount: Currency, Read Only.
grand_total: Currency, Read Only.
currency: Link → Currency, Mandatory.
payable_account: Link → Account, Mandatory.
cost_center: Link → Cost Center, Optional.
amended_from: Link → Expense Claim, Read Only.

Child Tables
expenses: Table → Expense Claim Detail, Mandatory.
advances: Table → Expense Claim Advance, Optional.
taxes: Table → Expense Taxes and Charges, Optional.
