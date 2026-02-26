Module Name: Employee Property History
Module: HRMS / HR
Type: Child Table (of Employee Promotion / Employee Transfer)
DocStatus: No

Description
Stores a single property change record (field name, old value, new value) to track what was changed during a promotion or transfer event.

Parent
Employee Promotion (field: promotion_details)
Employee Transfer (field: transfer_details)

Dependencies
None

Schema Fields
property: Data, Mandatory (the field name that changed, e.g. "designation").
current: Data, Optional (old value).
new: Data, Optional (new value).
