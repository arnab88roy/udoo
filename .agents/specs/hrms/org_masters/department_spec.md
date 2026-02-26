Module Name: Department
Module: HRMS / Core Masters
Type: Master (Tree structure)
DocStatus: No

Description
A core foundational table representing the organizational hierarchy of the company. Supports nested/tree structure via self-referencing parent key.

Dependencies
- Company

Schema Fields
department_name: Data, Mandatory, Unique.
parent_department: Link → Department, Optional (self-referencing, enables tree hierarchy).
company: Link → Company, Mandatory.
is_group: Check, Default: 0 (marks a node as a parent/group node).
disabled: Check, Default: 0.
