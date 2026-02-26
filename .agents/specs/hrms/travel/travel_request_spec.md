Module Name: Travel Request
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
An employee request to undertake business travel. Captures the purpose, destinations, dates, and estimated costs. On approval, creates Expense Claims for reimbursement.

Dependencies
- Employee
- Company
- Department
- Purpose of Travel (travel/)

Schema Fields
employee: Link → Employee, Mandatory.
employee_name: Data, Read Only.
department: Link → Department, Read Only.
company: Link → Company, Mandatory.
purpose_of_travel: Link → Purpose of Travel, Optional.
travel_from_date: Date, Mandatory.
travel_to_date: Date, Mandatory.
description: Small Text, Optional.
travel_type: Select (Domestic, International), Optional.
mode_of_transport: Select (Airways, Railways, Roadways, Waterways), Optional.
amended_from: Link → Travel Request, Read Only.

Child Tables
itinerary: Table → Travel Itinerary.
costing: Table → Travel Request Costing.
