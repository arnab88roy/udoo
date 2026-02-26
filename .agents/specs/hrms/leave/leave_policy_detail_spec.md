Module Name: Leave Policy Detail
Module: HRMS / HR
Type: Child Table (of Leave Policy)
DocStatus: No

Description
A single row within a Leave Policy defining the number of days annually allocated for a specific leave type.

Parent
Leave Policy (field: leave_policy_details)

Dependencies
- Leave Type (leave/)

Schema Fields
leave_type: Link → Leave Type, Mandatory.
annual_allocation: Float, Mandatory.
