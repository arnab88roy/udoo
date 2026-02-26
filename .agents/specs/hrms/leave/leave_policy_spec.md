Module Name: Leave Policy
Module: HRMS / HR
Type: Transactional (Submittable)
DocStatus: Yes (0=Draft, 1=Submitted, 2=Cancelled)

Description
A named bundle of leave entitlements, specifying how many days of each Leave Type are allocated annually. Submitted policies are assigned to employees.

Dependencies
- Leave Type (leave/)

Schema Fields
title: Data, Mandatory.
amended_from: Link → Leave Policy, Read Only.

Child Tables
leave_policy_details: Table → Leave Policy Detail, Mandatory.
