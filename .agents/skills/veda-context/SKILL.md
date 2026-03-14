# SKILL: VEDA Active Record Context

## What Is Active Record Context
Every message sent to VEDA includes the currently open record.
This is passed automatically — the user never needs to specify it.

## Context Schema
```python
{
  "open_record_type": "employee",  # or "leave_application", "salary_slip", "invoice", etc.
  "open_record_id": "uuid",        # the specific record open in the right panel / center card
  "open_module": "hrms",           # or "finance", "payroll", "settings"
  "tenant_id": "uuid"              # always present, extracted from JWT — never from request body
}
```

## How LangGraph Uses Context
The supervisor agent ALWAYS reads context before routing.

Examples:
- `open_record_type = "employee"` + user says "show leaves" →
  HR agent calls `GET /api/leave-applications/?employee_id={open_record_id}`
  NOT a general leave list — context pins the query.

- `open_record_type = "employee"` + user says "What's his balance?" →
  No disambiguation needed. VEDA operates on the open employee.

- `open_record_type = "employee"` + user says "Update his salary" →
  VEDA operates on `open_record_id` directly — no name required.

- `open_record_type = "leave_application"` + user says "Approve it" →
  VEDA calls `POST /api/leave-applications/{open_record_id}/approve`

## When Context Is Null
If no record is open (e.g. user is on the home dashboard):
```python
{"open_record_type": null, "open_record_id": null, "open_module": null, "tenant_id": "uuid"}
```
VEDA must ask for clarification before any record-specific operation.
Example: "Which employee would you like to update?" before patching.

Never assume record identity when open_record_id is null.

## Context Changes
When the user opens a different record, context updates automatically.
LangGraph receives fresh context on every message — it is not cached.

VEDA should acknowledge context switches when relevant:
- "I can see you've switched to Priya's record. What would you like to do?"
- Do NOT acknowledge switches for every message — only when it changes the task.

## What Context Is NOT
Context is not a memory store. It is a real-time signal.
Do not persist context between conversations.
Do not infer context from conversation history — read the live context field.

## VEDARequest Schema (Backend)
```python
class VEDARequest(BaseModel):
    message: str = Field(description="The user's natural language input")
    context: UIContext = Field(description="The currently active record in the UI")
    conversation_history: List[dict] = Field(
        default=[],
        description="Last 10 messages (role + content) for conversational continuity"
    )
    # tenant_id comes from JWT — NOT accepted from request body
```

The `tenant_id` in UIContext must always be overwritten server-side from the JWT.
Client-supplied tenant_id in context is ignored.

## LangGraph Node Pattern
```python
def supervisor_node(state: AgentState) -> AgentState:
    context = state["context"]
    message = state["message"]

    # Context-aware routing
    if context.open_record_type == "leave_application":
        return route_to_hr_agent(state, hint="leave_operation")
    elif context.open_record_type == "salary_slip":
        return route_to_payroll_agent(state)
    elif context.open_module == "finance":
        return route_to_finance_agent(state)
    else:
        return classify_intent(state)  # general routing
```

## Context Factory Functions

Never construct UIContext manually in agent code.
Always use one of these helpers from app.utils.veda_context:

| Function | When to use |
|---|---|
| `null_context(tenant_id)` | Background tasks, home dashboard, system notifications |
| `context_for_module(tenant_id, module)` | Agent routed to a module, no record open yet |
| `context_for_record(tenant_id, type, id, module)` | Specific record has been identified |
| `sanitise_request_context(ctx, jwt_tenant)` | At the TOP of every VEDA endpoint — always first line |
| `context_matches_type(ctx, type)` | Guard before assuming open record type in LangGraph node |
| `is_record_context_active(ctx)` | Check if any record is open at all |
| `describe_context(ctx)` | Inject into LangGraph system prompt for context awareness |
| `build_context(tenant_id, ...)` | General purpose — when none of the above fit |

## LangGraph Agent Pattern

Every LangGraph agent node that handles a VEDA request
must follow this pattern:

```python
async def hr_agent_node(state: AgentState) -> AgentState:
    context = state["context"]   # already sanitised by the endpoint
    message = state["message"]

    # Step 1: Guard — check if we have the record we need
    if context_matches_type(context, "employee"):
        # Operate on the open employee record directly
        employee_id = context.open_record_id
    else:
        # No employee context — search by name from the message
        # or ask for clarification
        employee_id = await resolve_employee_from_message(message, context.tenant_id)

    # Step 2: Build response context
    if employee_id:
        response_context = context_for_record(
            context.tenant_id, "employee", employee_id, "hrms"
        )
    else:
        response_context = context_for_module(context.tenant_id, "hrms")

    # Step 3: Return UIResponse with correct context
    ...
```
