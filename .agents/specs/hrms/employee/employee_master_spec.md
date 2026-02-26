Module Name: Employee
Module: HRMS / Core Masters
Type: Master (Transactional)
DocStatus: No

Description
The central master record for every employee, storing personal, professional, contact, and exit information. The primary FK target across all HRMS transactional documents.

Dependencies
- Gender (core_masters)
- Salutation (core_masters)
- Holiday List (core_masters)
- Company
- Department (org_masters)
- Designation (org_masters)
- Branch (org_masters)
- Employment Type (org_masters)
- Employee Grade (org_masters)
- Employee (self-referencing, for reports_to hierarchy)
- User (Core Masters, for system login linkage)
- Currency

Schema Fields
--- Basic Info ---
naming_series: Select, Default: HR-EMP-.
first_name: Data, Mandatory.
middle_name: Data, Optional.
last_name: Data, Optional.
employee_name: Data, Read Only (computed full name).
salutation: Link → Salutation, Optional.
gender: Link → Gender, Mandatory.
date_of_birth: Date, Mandatory.
image: Attach Image, Optional.
employee_number: Data, Optional.

--- Status & System ---
status: Select (Active, Inactive, Suspended, Left), Mandatory, Default: Active.
user_id: Link → User, Optional.
create_user_permission: Check, Default: 1.

--- Company Details ---
company: Link → Company, Mandatory.
department: Link → Department, Optional.
designation: Link → Designation, Optional.
reports_to: Link → Employee, Optional (self-referencing).
branch: Link → Branch, Optional.
employment_type: Link → Employment Type, Optional.
employee_grade: Link → Employee Grade, Optional.

--- Joining & Contract ---
date_of_joining: Date, Mandatory.
scheduled_confirmation_date: Date, Optional (Offer Date).
final_confirmation_date: Date, Optional (Confirmation Date).
contract_end_date: Date, Optional.
notice_number_of_days: Int, Optional.
date_of_retirement: Date, Optional.

--- Attendance & Leave ---
attendance_device_id: Data, Optional, Unique.
holiday_list: Link → Holiday List, Optional.

--- Salary ---
salary_mode: Select (Bank, Cash, Cheque), Optional.
salary_currency: Link → Currency, Optional.
ctc: Currency, Optional.
bank_name: Data, Optional (shown if salary_mode = Bank).
bank_ac_no: Data, Optional (shown if salary_mode = Bank).
iban: Data, Optional (shown if salary_mode = Bank).

--- Contact ---
cell_number: Data, Optional.
company_email: Data (Email), Optional.
personal_email: Data (Email), Optional.
prefered_contact_email: Select (Company Email, Personal Email, User ID), Optional.
prefered_email: Data, Read Only.
unsubscribed: Check, Default: 0.

--- Address ---
current_address: Small Text, Optional.
current_accommodation_type: Select (Rented, Owned), Optional.
permanent_address: Small Text, Optional.
permanent_accommodation_type: Select (Rented, Owned), Optional.

--- Emergency Contact ---
person_to_be_contacted: Data, Optional.
emergency_phone_number: Data (Phone), Optional.
relation: Data, Optional.

--- Personal Details ---
marital_status: Select (Single, Married, Divorced, Widowed), Optional.
blood_group: Select (A+, A-, B+, B-, AB+, AB-, O+, O-), Optional.
family_background: Small Text, Optional.
health_details: Small Text, Optional.
passport_number: Data, Optional.
date_of_issue: Date, Optional.
valid_upto: Date, Optional.
place_of_issue: Data, Optional.
bio: Text Editor, Optional.

--- Employee Exit ---
resignation_letter_date: Date, Optional.
relieving_date: Date, Mandatory if status = Left.
reason_for_leaving: Small Text, Optional.
leave_encashed: Select (Yes, No), Optional.
encashment_date: Date, Optional (shown if leave_encashed = Yes).
held_on: Date, Optional (Exit Interview Held On).
new_workplace: Data, Optional.
feedback: Small Text, Optional.

Child Tables
education: Table → Employee Education.
external_work_history: Table → Employee External Work History.
internal_work_history: Table → Employee Internal Work History.
