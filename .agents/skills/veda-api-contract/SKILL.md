---
name: VEDA-api-contract
description: Rules for making FastAPI endpoints and Pydantic schemas consumable by the VEDA agent.
---

# Skill: VEDA API Contract

The VEDA agent calls the same FastAPI endpoints a human uses.
For VEDA to work accurately, every schema and endpoint must be self-describing.
If a field or endpoint is ambiguous to a human reading it cold, it is ambiguous to the AI.

## 1. Every Pydantic Field Must Have a Description
This is non-negotiable. The AI reads field descriptions to understand what to populate.

```python
# WRONG
attendance_date: date

# CORRECT
attendance_date: date = Field(
    ...,
    description="The specific date for this attendance record. Format: YYYY-MM-DD. One record per employee per date — duplicates will be rejected."
)

# WRONG
docstatus: int = 0

# CORRECT
docstatus: int = Field(
    0,
    description="Workflow state. 0=Draft (editable), 1=Submitted (locked), 2=Cancelled (terminal). Never set manually — use /submit or /cancel endpoints."
)
```

## 2. Every Endpoint Must Have a Docstring
State machine endpoints must document valid prior states:

```python
@router.post("/{id}/submit")
async def submit_attendance(id: UUID, ...):
    """
    Submit an Attendance record for approval.
    Transitions docstatus from 0 (Draft) to 1 (Submitted).
    Raises 400 if record is not in Draft state.
    """
```

## 3. Enum Fields Must Use Literal Types or Enums
Never use bare `str` for fields with fixed valid values.
The AI must know what values are valid without guessing:

```python
# WRONG
status: str

# CORRECT
status: Literal["Present", "Absent", "Half Day", "On Leave", "Work From Home"] = Field(
    "Present",
    description="Attendance status for the day."
)
```

## 4. Response Schemas Must Be Complete
The AI makes decisions based on response data.
Every response schema must include all fields needed for the next decision:

- Attendance response must include `employee_name` so AI can confirm correct employee
- LeaveApplication response must include `total_leave_days` so AI can report the balance impact
- SalarySlip response must include `net_pay` so AI can present the payroll summary

## 5. Consistent Naming Across All Modules
The AI learns patterns. Inconsistent naming breaks its ability to generalise.

| Concept | Correct name | Never use |
|---|---|---|
| Create record | `POST /<module>/` | `POST /<module>/create` |
| Submit workflow | `POST /<module>/{id}/submit` | `POST /<module>/{id}/approve`, `/confirm`, `/finalize` |
| Cancel workflow | `POST /<module>/{id}/cancel` | `POST /<module>/{id}/void`, `/delete`, `/reverse` |
| List records | `GET /<module>/` | `GET /<module>/list`, `/all` |
| Single record | `GET /<module>/{id}` | `GET /<module>/get/{id}` |

## 6. The VEDA Decision Loop
When the AI needs to complete a task, it follows this pattern:
1. **Fetch** — GET relevant records to understand current state
2. **Validate** — Check required fields are present and state is correct
3. **Pause** — If anything is missing or ambiguous, ask the human
4. **Execute** — POST/PATCH to create or transition
5. **Confirm** — GET the result and present a human-readable summary
6. **Await** — Wait for human approval before any submit/cancel action

Your API must support all 6 steps cleanly.