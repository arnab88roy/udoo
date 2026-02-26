Module Name: Leave Period
Module: HRMS / HR
Type: Master
DocStatus: No

Description
Defines a fiscal or calendar period (e.g., Jan–Dec 2025) during which leave allocations are valid. Used as a reference in Leave Allocation and Leave Policy Assignment.

Dependencies
- Company
- Holiday List (for optional holiday assignment)

Schema Fields
from_date: Date, Mandatory.
to_date: Date, Mandatory.
is_active: Check, Default: 0.
company: Link → Company, Mandatory.
optional_holiday_list: Link → Holiday List, Optional.
