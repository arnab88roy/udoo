Module Name: Appraisal KRA
Module: HRMS / HR
Type: Child Table (of Appraisal)
DocStatus: No

Description
A single KRA rating row in an Appraisal, capturing the score and weight for each KRA.

Parent
Appraisal (field: appraisal_kra)

Dependencies
- KRA (performance/)

Schema Fields
kra: Link → KRA, Mandatory.
per_weightage: Float, Mandatory.
score: Float, Optional.
score_earned: Float, Read Only.
