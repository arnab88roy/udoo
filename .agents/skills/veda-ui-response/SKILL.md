# SKILL: VEDA UI Response Contract

## Rule 1 — Always Return UIResponse
VEDA must NEVER return plain text for actions that affect the database.
Every response that involves data must be a typed UIResponse.

## Rule 2 — Response Type Selection
- User asks to SEE data → TABLE
- User asks to VIEW or EDIT a specific record → FORM
- User needs to approve/reject a record → APPROVAL
- VEDA cannot proceed without human input → BLOCKER
- VEDA is about to execute irreversible action → CONFIRM
- VEDA is processing a long task → PROGRESS
- Simple acknowledgement or greeting → TEXT

## Rule 3 — Actions
Every UIResponse that requires a follow-up action must include
UIAction objects. Never embed action instructions in the message text.

## Rule 4 — Audit Note
Any UIResponse that modifies data must include an audit_note.
This is written to the audit log with VEDA attribution.

## Rule 5 — Confidence
Include veda_confidence (0.0-1.0) whenever VEDA infers something
rather than reading it directly from the database.
Example: inferring department from designation = 0.75 confidence.
This renders as a visual indicator on the form field.

---

## Payload Shapes

### TABLE
```json
{
  "type": "table",
  "message": "Here are the active employees:",
  "payload": {
    "columns": ["name", "department", "status"],
    "rows": [...],
    "total": 22
  },
  "actions": [
    {"label": "Export", "style": "secondary", "action_id": "export", "endpoint": "/api/employees/export", "method": "POST", "payload": {}, "confirmation_required": false},
    {"label": "Add Employee", "style": "primary", "action_id": "add_employee", "endpoint": "/api/employees/", "method": "POST", "payload": {}, "confirmation_required": false}
  ],
  "context": {"open_record_type": null, "open_record_id": null, "open_module": "hrms", "tenant_id": "uuid"},
  "veda_confidence": null,
  "audit_note": null
}
```

### FORM
```json
{
  "type": "form",
  "message": "Here is Dev Patel's employee record:",
  "payload": {
    "record_type": "employee",
    "record_id": "uuid",
    "fields": [
      {"name": "first_name", "label": "First Name", "type": "text", "required": true},
      {"name": "department_id", "label": "Department", "type": "select", "required": true}
    ],
    "values": {
      "first_name": "Dev",
      "department_id": "uuid"
    }
  },
  "actions": [
    {"label": "Save", "style": "primary", "action_id": "save", "endpoint": "/api/employees/uuid", "method": "PATCH", "payload": {}, "confirmation_required": false}
  ],
  "context": {"open_record_type": "employee", "open_record_id": "uuid", "open_module": "hrms", "tenant_id": "uuid"},
  "veda_confidence": null,
  "audit_note": null
}
```

### APPROVAL
```json
{
  "type": "approval",
  "message": "Dev Patel has requested 3 days of Casual Leave.",
  "payload": {
    "record_type": "leave_application",
    "record_id": "uuid",
    "summary": {
      "employee": "Dev Patel",
      "leave_type": "Casual Leave",
      "dates": "Mar 18-20, 2026",
      "balance_after": "7 days remaining"
    },
    "action_options": ["Approve", "Reject", "Ask for reason"]
  },
  "actions": [
    {"label": "Approve", "style": "primary", "action_id": "approve", "endpoint": "/api/leave-applications/uuid/approve", "method": "POST", "payload": {}, "confirmation_required": false},
    {"label": "Reject", "style": "danger", "action_id": "reject", "endpoint": "/api/leave-applications/uuid/reject", "method": "POST", "payload": {}, "confirmation_required": false}
  ],
  "context": {"open_record_type": "leave_application", "open_record_id": "uuid", "open_module": "hrms", "tenant_id": "uuid"},
  "veda_confidence": null,
  "audit_note": "Leave approval decision recorded by VEDA on behalf of manager."
}
```

### BLOCKER
```json
{
  "type": "blocker",
  "message": "I cannot process Suresh's payslip.",
  "payload": {
    "reason": "Bank account changed 3 days ago. Policy requires 7-day wait or second-level approval.",
    "resolution_options": [
      {"label": "Request second-level approval", "style": "primary", "action_id": "escalate", "endpoint": "/api/approvals/escalate", "method": "POST", "payload": {"record_id": "uuid"}, "confirmation_required": false},
      {"label": "Skip this employee", "style": "secondary", "action_id": "skip", "endpoint": "", "method": "POST", "payload": {}, "confirmation_required": false}
    ]
  },
  "actions": [],
  "context": {"open_record_type": "salary_slip", "open_record_id": "uuid", "open_module": "payroll", "tenant_id": "uuid"},
  "veda_confidence": null,
  "audit_note": null
}
```

### CONFIRM
```json
{
  "type": "confirm",
  "message": "I'm about to submit payroll for March 2026. This will lock 47 salary slips.",
  "payload": {
    "summary": {
      "month": "March 2026",
      "employees": 47,
      "total_net_pay": "₹32,45,000"
    },
    "warning": "Submitted slips cannot be edited. They can only be cancelled.",
    "is_irreversible": false
  },
  "actions": [
    {"label": "Confirm & Submit", "style": "primary", "action_id": "confirm_submit", "endpoint": "/api/salary-slips/bulk-submit", "method": "POST", "payload": {"month": 3, "year": 2026}, "confirmation_required": false},
    {"label": "Cancel", "style": "ghost", "action_id": "cancel", "endpoint": "", "method": "POST", "payload": {}, "confirmation_required": false}
  ],
  "context": {"open_record_type": null, "open_record_id": null, "open_module": "payroll", "tenant_id": "uuid"},
  "veda_confidence": null,
  "audit_note": "Bulk payroll submission confirmed by user."
}
```

### PROGRESS
```json
{
  "type": "progress",
  "message": "Generating payroll for March 2026...",
  "payload": {
    "steps": [
      {"label": "Fetching employees", "status": "completed"},
      {"label": "Calculating salaries", "status": "in_progress"},
      {"label": "Applying statutory deductions", "status": "pending"},
      {"label": "Creating salary slips", "status": "pending"}
    ],
    "current_step": 1,
    "percent": 35
  },
  "actions": [],
  "context": {"open_record_type": null, "open_record_id": null, "open_module": "payroll", "tenant_id": "uuid"},
  "veda_confidence": null,
  "audit_note": null
}
```

### TEXT
```json
{
  "type": "text",
  "message": "Hello! I'm VEDA, your AI business assistant. What would you like to do today?",
  "payload": {
    "content": "Hello! I'm VEDA, your AI business assistant. What would you like to do today?",
    "hints": ["Show pending leaves", "Run payroll for this month", "Add a new employee"]
  },
  "actions": [],
  "context": {"open_record_type": null, "open_record_id": null, "open_module": null, "tenant_id": "uuid"},
  "veda_confidence": null,
  "audit_note": null
}
```
