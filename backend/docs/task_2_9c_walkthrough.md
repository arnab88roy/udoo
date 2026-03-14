# Task 2.9c Walkthrough — Active Record Context System

## Overview
This task completed the VEDA context lifecycle by implementing a centralized utility module for context construction, validation, and security sanitization. This system ensures that VEDA agents always have awareness of the user's active record while strictly enforcing tenant boundaries.

## Changes Made

### 1. VEDA Context Utility
Created `backend/app/utils/veda_context.py` with the following helpers:
- `build_context`: General purpose context builder.
- `null_context`: For background tasks or home dashboard states.
- `context_for_module`: Scopes context to a module (e.g., 'hrms').
- `context_for_record`: Scopes context to a specific entity (e.g., 'employee').
- `sanitise_request_context`: **CRITICAL**: Overwrites client-supplied tenant_id with server-side JWT value.
- `is_record_context_active`: Checks if a specific record is being viewed.
- `context_matches_type`: Guard for agent logic (prevents operating on wrong record type).
- `describe_context`: Generates human-readable context descriptions for AI system prompts.

### 2. Main API Integration
Updated `/api/veda/chat` in `backend/app/main.py`:
- Now automatically sanitizes incoming context.
- Returns the human-readable context description in the stub response to prove correct flow.

### 3. Documentation & Skills
- Updated `veda-context` SKILL.md with a factory function reference table.
- Documented the standard LangGraph agent pattern for utilizing context safely.

## Verification Results

### Gate 1: Import Check
```bash
# Result: All imports OK
```

### Gate 2: Unit Tests (pytest)
Executed 9 tests covering all helpers and security boundaries.
```bash
# Result: 9 passed
```

### Gate 3 & 4: Context Flow Smoke Tests
#### Active Context (Employee Record)
**Input Context**: `employee`, ID: `66ddb47a...`
**Resulting Message**:
> "VEDA received: 'Show her leaves'. Context: The user currently has a employee record (ID: 66ddb47a-...) open in the hrms module. ..."

#### Null Context (Home Dashboard)
**Input Context**: `null`
**Resulting Message**:
> "VEDA received: 'Hello VEDA'. Context: No record is currently open. The user is on the home dashboard. ..."

### Gate 5: Security Test (Tenant Spoofing)
Verified that providing a fake `tenant_id` in the request body is correctly overwritten by the JWT value.
```bash
# Result: Security gate passed — tenant spoofing blocked
```

## Factory Reference Table

| Function | Intent |
|---|---|
| `null_context` | System notifications / Home |
| `context_for_module` | Module interaction |
| `context_for_record` | Specific record interaction |
| `sanitise_request_context` | Security boundary |
| `describe_context` | Agent prompt injection |
