Module Name: Employee Advance
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
Tracks cash advances issued to an employee for business purposes (e.g., for a trip). Gets reconciled when linked Expense Claims are submitted.

Dependencies
- Employee
- Company
- Department
- Account (Finance)
- Currency

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only.
company: Link → Company, Mandatory.
posting_date: Date, Mandatory, Default: Today.
purpose: Small Text, Mandatory.
advance_amount: Currency, Mandatory.
advance_account: Link → Account, Mandatory.
mode_of_payment: Link → Mode of Payment, Optional.
currency: Link → Currency, Mandatory.
claimed_amount: Currency, Read Only.
returned_amount: Currency, Read Only.
status: Select (Draft, Issued, Paid, Claimed, Cancelled), Read Only.
remarks: Small Text, Optional.
amended_from: Link → Employee Advance, Read Only.
