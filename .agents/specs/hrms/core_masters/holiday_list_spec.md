Module Name: Holiday List
Module: HRMS / HR
Type: Master
DocStatus: No

Description
Defines a named calendar of public and company holidays for a given year. Assigned to employees and departments to determine working days.

Dependencies
- Company

Schema Fields
holiday_list_name: Data, Mandatory, Unique.
from_date: Date, Mandatory.
to_date: Date, Mandatory.
company: Link → Company, Mandatory.
weekly_off: Select, Mandatory.
total_holidays: Int, Read Only.

Child Tables
holidays: Table → Holiday (holiday_date: Date, description: Data, weekly_off: Check)
