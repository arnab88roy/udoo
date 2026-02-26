Module Name: Leave Block List
Module: HRMS / HR
Type: Master
DocStatus: No

Description
Defines a list of dates on which employees cannot submit leave applications. Can be scoped to the whole company or individual departments.

Dependencies
- Company
- Leave Type (leave/)

Schema Fields
leave_block_list_name: Data, Mandatory, Unique.
company: Link → Company, Mandatory.
applies_to_all_departments: Check, Default: 0 (if 0, must be assigned to departments manually).
leave_type: Link → Leave Type, Optional.

Child Tables
leave_block_list_dates: Table → Leave Block List Date, Mandatory.
leave_block_list_allowed: Table → Leave Block List Allow, Optional.
