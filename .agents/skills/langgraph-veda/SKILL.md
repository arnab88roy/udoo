---
name: langgraph-veda
description: Rules for implementing the VEDA AI layer using LangGraph. Defines graph
  structure, state schema, tool patterns, Claude integration, and response handling.
---

# Skill: LangGraph VEDA Architecture

## 1. Dependencies

Add these to `requirements.txt`:
```
langgraph>=0.0.40
langchain-anthropic>=0.1.0
anthropic>=0.21.0
```

Standard import block used across all VEDA files:
```python
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
```

---

## 2. Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    POST /api/veda/chat                       │
│                           ↓                                  │
│   VEDARequest { message, context, conversation_history }     │
│                           ↓                                  │
│              sanitise_request_context()                      │
│              get_current_user()                              │
│                           ↓                                  │
│              ┌────────────────────────┐                      │
│              │   build_initial_state  │                      │
│              └───────────┬────────────┘                      │
│                          ↓                                   │
│              ┌────────────────────────┐                      │
│              │      SUPERVISOR        │                      │
│              │  (classify + route)    │                      │
│              └───────────┬────────────┘                      │
│                          ↓                                   │
│         ┌────────────────┼────────────────┐                  │
│         ↓                ↓                ↓                  │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│   │ HR Agent │    │ Payroll  │    │ Finance  │               │
│   │ (Task    │    │ (future) │    │ (future) │               │
│   │  3.1)    │    │          │    │          │               │
│   └────┬─────┘    └──────────┘    └──────────┘               │
│        ↓                                                     │
│   ┌──────────┐                                               │
│   │  Tools   │                                               │
│   └────┬─────┘                                               │
│        ↓                                                     │
│     UIResponse                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. File Structure

Create this exact directory structure under `backend/app/veda/`:

```
backend/app/veda/
├── __init__.py
├── state.py          # AgentState TypedDict + build_initial_state()
├── graph.py          # StateGraph construction + veda_graph singleton
├── supervisor.py     # supervisor_node + classify_intent() + _get_hints_for_role()
├── prompts.py        # describe_user() — assembles VEDA system prompt context
├── agents/
│   ├── __init__.py
│   └── hr_agent.py   # hr_agent_node + HR_TOOLS registry
└── tools/
    ├── __init__.py
    └── hr_tools.py   # list_employees_tool (first tool for Task 3.1)
```

---

## 4. State Schema

File: `backend/app/veda/state.py`

```python
from typing import TypedDict, List, Optional, Literal
from uuid import UUID

from app.schemas.ui_response import UIContext, UIResponse
from app.schemas.user_context import UserContext


class AgentState(TypedDict):
    """
    State object passed through all LangGraph nodes.

    Immutable fields (set once at entry, never modified):
        message: User's natural language input
        context: Active record context from frontend (sanitised)
        user: Authenticated user from JWT
        conversation_history: Last 10 messages for continuity
        tenant_id: Always equals user.tenant_id — explicit for clarity

    Mutable fields (set by nodes as the graph executes):
        current_agent: Which agent the supervisor routed to
        tool_name: Which tool was selected
        tool_params: Parameters extracted for the tool
        response: Final UIResponse — set this to terminate routing
        error: Error message if something failed
    """
    # Immutable input
    message: str
    context: UIContext
    user: UserContext
    conversation_history: List[dict]
    tenant_id: UUID

    # Routing state (set by supervisor)
    current_agent: Optional[Literal["hr", "payroll", "finance", "setup"]]
    tool_name: Optional[str]
    tool_params: Optional[dict]

    # Output (set by agents)
    response: Optional[UIResponse]
    error: Optional[str]


def build_initial_state(
    message: str,
    context: UIContext,
    user: UserContext,
    conversation_history: List[dict],
) -> AgentState:
    """
    Factory function. Creates the initial state at graph entry.
    Called from /api/veda/chat endpoint after context sanitisation.
    Enforces the 10-message conversation history limit here — not in the endpoint.
    """
    return AgentState(
        message=message,
        context=context,
        user=user,
        conversation_history=conversation_history[-10:],
        tenant_id=user.tenant_id,
        current_agent=None,
        tool_name=None,
        tool_params=None,
        response=None,
        error=None,
    )
```

---

## 5. Graph Construction

File: `backend/app/veda/graph.py`

```python
from langgraph.graph import StateGraph, END
from app.veda.state import AgentState
from app.veda.supervisor import supervisor_node
from app.veda.agents.hr_agent import hr_agent_node
# Phase 3.3: from app.veda.agents.payroll_agent import payroll_agent_node
# Phase 3.4: from app.veda.agents.finance_agent import finance_agent_node


def build_veda_graph() -> StateGraph:
    """
    Constructs the VEDA LangGraph. Call once at startup.

    Routing rules:
    - supervisor_node sets state["response"] directly for: greetings, blockers,
      permission denials, and any agent not yet implemented.
    - supervisor_node sets state["current_agent"] for agents that are implemented.
    - route_to_agent() reads those fields and returns the correct edge key.
    - Any unimplemented agent falls through to END via the supervisor's blocker.
    """
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("hr_agent", hr_agent_node)
    # Phase 3.3: graph.add_node("payroll_agent", payroll_agent_node)
    # Phase 3.4: graph.add_node("finance_agent", finance_agent_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "hr": "hr_agent",
            "end": END,
        }
    )

    graph.add_edge("hr_agent", END)
    # Phase 3.3: graph.add_edge("payroll_agent", END)
    # Phase 3.4: graph.add_edge("finance_agent", END)

    return graph.compile()


def route_to_agent(state: AgentState) -> str:
    """
    Routing function for conditional edges after supervisor.

    Returns "end" in ALL of these cases:
    - supervisor already set state["response"] (greeting, blocker, permission denial)
    - current_agent is payroll or finance (not yet implemented — supervisor handles)
    - current_agent is None or unrecognised

    Returns "hr" only when current_agent == "hr" AND no response is set.
    """
    # Supervisor already resolved the request
    if state.get("response") is not None:
        return "end"

    agent = state.get("current_agent")
    if agent == "hr":
        return "hr"

    # payroll, finance, setup, None — not yet implemented
    # Supervisor is responsible for setting a BLOCKER response for these
    # before routing reaches here. If it somehow doesn't, end safely.
    return "end"


# Compiled singleton — import this in main.py
veda_graph = build_veda_graph()
```

---

## 6. Prompts

File: `backend/app/veda/prompts.py`

This file has one responsibility: convert a `UserContext` into a human-readable
string that gets injected into every Claude system prompt. This is how VEDA knows
who it is talking to, what they can do, and what they can see.

```python
from app.schemas.user_context import UserContext


def describe_user(user: UserContext) -> str:
    """
    Returns a structured string describing the authenticated user.
    Injected into Claude system prompts in supervisor and agent nodes.

    Output example for an owner:
        "The user is Arnab Roy (role: owner).
         They have full access to all modules: HRMS, Payroll, Finance, Settings.
         They can see all employees across the organisation."

    Output example for a manager:
        "The user is Priya Sharma (role: manager).
         They have view and approve access to HRMS for their team only.
         They have no access to Payroll or Finance.
         They can only see employees who report to them directly or indirectly."

    Output example for an employee:
        "The user is Dev Patel (role: employee).
         They have self-service access only: their own leave, attendance, and payslips.
         They cannot view other employees."
    """
    # Role-to-access description map
    access_descriptions = {
        "owner": (
            "They have full access to all modules: HRMS, Payroll, Finance, and Settings. "
            "They can see all employees across the organisation."
        ),
        "hr_manager": (
            "They have full access to HRMS and Payroll. "
            "They have no access to Finance. "
            "They can see all employees across the organisation."
        ),
        "finance_manager": (
            "They have full access to Finance. "
            "They have view-only access to Payroll. "
            "They have no access to HRMS or employee records."
        ),
        "manager": (
            "They have view and approve access to HRMS for their team only. "
            "They have no access to Payroll or Finance. "
            "They can only see employees who report to them directly or indirectly."
        ),
        "employee": (
            "They have self-service access only: their own leave, attendance, and payslips. "
            "They cannot view other employees' records."
        ),
        "auditor": (
            "They have read-only access to all modules. "
            "They cannot create, edit, submit, or approve any record."
        ),
    }

    name = getattr(user, "full_name", None) or getattr(user, "name", None) or "the user"
    role = user.role
    access = access_descriptions.get(role, f"They have {role} level access.")

    return (
        f"The user is {name} (role: {role}). "
        f"{access}"
    )
```

---

## 7. Supervisor Node

File: `backend/app/veda/supervisor.py`

`classify_intent` lives here — do not create a separate file for it.

```python
import os
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from app.veda.state import AgentState
from app.veda.prompts import describe_user
from app.utils.veda_context import describe_context
from app.utils.permissions import check_permission
from app.schemas.ui_response import make_text_response, make_blocker_response
from app.schemas.user_context import UserContext


# Claude client — initialised once, reused across all calls
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=1024,
)


async def classify_intent(
    message: str,
    user_description: str,
    context_description: str,
    conversation_history: list,
) -> dict:
    """
    Uses Claude to classify user intent and extract parameters.

    Returns a dict with keys:
        agent:      "hr" | "payroll" | "finance" | "setup" | "greeting"
        tool:       tool name string, or None for greetings
        params:     dict of extracted parameters (may be empty)
        confidence: float 0.0–1.0

    On JSON parse failure, returns a safe greeting fallback.
    """
    system = f"""You are VEDA's intent classifier for an Indian SME ERP system.

{user_description}

{context_description}

Classify the user's message and respond in JSON only.
Do not include any explanation, preamble, or markdown fences. Raw JSON only.

Classify into ONE agent:
- "hr"       — employee records, leave management, attendance
- "payroll"  — salary slips, payroll runs, deductions, PF/ESI
- "finance"  — invoices, quotes, payments, clients, GST
- "setup"    — company settings, departments, designations
- "greeting" — hello, thanks, general chat, help

For agent "hr", identify the tool:
- "list_employees"         — user wants a list of employees (e.g. "show employees", "who is active")
- "get_employee"           — user wants details on one specific employee (by name or ID)
- "list_leave_applications"— user wants to see leave requests
- "approve_leave"          — user wants to approve a leave request

Extract any parameters mentioned:
- For list_employees: {{ "status_filter": "Active" }} (default Active, or "Inactive" if mentioned)
- For get_employee:   {{ "name": "Dev Patel" }} or {{ "employee_id": "EMP-001" }}
- For approve_leave:  {{ "leave_id": "uuid-here" }} if mentioned

Response format (strict JSON, nothing else):
{{"agent": "hr", "tool": "list_employees", "params": {{"status_filter": "Active"}}, "confidence": 0.95}}
"""

    messages = [SystemMessage(content=system)]

    # Include conversation history for multi-turn continuity
    from langchain_core.messages import AIMessage
    for msg in conversation_history:
        if msg.get("role") == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg.get("role") == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=message))

    try:
        response = await llm.ainvoke(messages)
        return json.loads(response.content)
    except (json.JSONDecodeError, Exception):
        # Safe fallback — treat as greeting, never crash
        return {"agent": "greeting", "tool": None, "params": {}, "confidence": 0.5}


async def supervisor_node(state: AgentState) -> AgentState:
    """
    Entry point node. Classifies intent and routes to correct agent.

    Responsibilities:
    1. Build prompt context strings from user and active record context
    2. Classify intent using Claude
    3. Handle greetings directly (no agent needed)
    4. Check permissions before routing to any module
    5. Return BLOCKER for unimplemented agents (payroll, finance, setup)
    6. Set current_agent + tool_name + tool_params for implemented agents
    """
    user = state["user"]
    context = state["context"]
    message = state["message"]
    history = state["conversation_history"]

    user_description = describe_user(user)
    context_description = describe_context(context)

    classification = await classify_intent(
        message=message,
        user_description=user_description,
        context_description=context_description,
        conversation_history=history,
    )

    agent = classification.get("agent", "greeting")
    tool = classification.get("tool")
    params = classification.get("params", {})

    # ── Handle greetings directly ──────────────────────────────────────────
    if agent == "greeting":
        response = make_text_response(
            message="Hello! I'm VEDA, your AI business assistant. What would you like to do today?",
            context=context,
            hints=_get_hints_for_role(user),
        )
        return {**state, "response": response}

    # ── Map agent name to module name for permission checks ────────────────
    module_map = {
        "hr":      "hrms",
        "payroll": "payroll",
        "finance": "finance",
        "setup":   "settings",
    }
    module = module_map.get(agent)

    # ── Permission check ───────────────────────────────────────────────────
    if module and not check_permission(user, module, "view"):
        response = make_blocker_response(
            reason=(
                f"Your role ({user.role}) does not have access to the {module} module. "
                f"Contact your administrator if you need access."
            ),
            resolution_options=[],
            context=context,
            blocked_task=f"Accessing {module}",
        )
        return {**state, "response": response}

    # ── Block unimplemented agents (payroll, finance, setup) ───────────────
    # Remove this block when the corresponding agent is implemented.
    if agent in ("payroll", "finance", "setup"):
        response = make_blocker_response(
            reason=(
                f"The {agent} module is not yet available in VEDA. "
                f"It will be available soon."
            ),
            resolution_options=[],
            context=context,
            blocked_task=f"Accessing {agent}",
        )
        return {**state, "response": response}

    # ── Route to implemented agent ─────────────────────────────────────────
    return {
        **state,
        "current_agent": agent,
        "tool_name": tool,
        "tool_params": params,
    }


def _get_hints_for_role(user: UserContext) -> list:
    """Return role-appropriate hint chips shown below VEDA greetings."""
    if user.is_owner or user.is_hr_manager:
        return ["Show all employees", "Run payroll", "Pending approvals"]
    elif user.is_finance_manager:
        return ["Outstanding invoices", "Create quote", "Payment received"]
    elif user.is_manager:
        return ["My team", "Pending leave approvals", "Team attendance"]
    elif user.is_employee:
        return ["Apply for leave", "My payslips", "My attendance"]
    else:
        return ["Show dashboard"]
```

---

## 8. HR Tools

File: `backend/app/veda/tools/hr_tools.py`

```python
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr_masters import models
from app.schemas.user_context import UserContext
from app.schemas.ui_response import (
    UIContext,
    UIResponse,
    UIAction,
    make_table_response,
    make_blocker_response,
)
from app.utils.veda_context import context_for_module
from app.utils.org_scope import get_visible_employee_ids
from app.utils.permissions import check_permission


async def list_employees_tool(
    db: AsyncSession,
    user: UserContext,
    context: UIContext,
    status_filter: Optional[str] = "Active",
) -> UIResponse:
    """
    List employees visible to the current user.

    Permission required: hrms.view
    Org scope applied:
        owner / hr_manager / auditor  → all employees in tenant
        manager                       → direct + indirect reports only
        employee                      → self only
        finance_manager               → BLOCKER (no hrms access)

    Returns:
        TABLE UIResponse  — on success
        BLOCKER UIResponse — if no permission or no visible employees
    """
    # ── Step 1: Permission check ───────────────────────────────────────────
    if not check_permission(user, "hrms", "view"):
        return make_blocker_response(
            reason=f"Your role ({user.role}) does not have access to employee records.",
            resolution_options=[],
            context=context,
            blocked_task="Listing employees",
        )

    # ── Step 2: Org scope ──────────────────────────────────────────────────
    # Returns None  → no filter, user can see everyone
    # Returns []    → empty list, user can see no one (should not happen if perm check passed)
    # Returns [ids] → filter to this list
    visible_ids = await get_visible_employee_ids(db, user, user.tenant_id)

    if visible_ids is not None and len(visible_ids) == 0:
        return make_blocker_response(
            reason="You do not have any employees in your reporting scope.",
            resolution_options=[],
            context=context,
            blocked_task="Listing employees",
        )

    # ── Step 3: Query with tenant isolation ───────────────────────────────
    query = (
        select(models.Employee)
        .where(models.Employee.tenant_id == user.tenant_id)
    )

    if status_filter:
        query = query.where(models.Employee.status == status_filter)

    if visible_ids is not None:
        query = query.where(models.Employee.id.in_(visible_ids))

    query = query.order_by(models.Employee.employee_name)

    # ── Step 4: Execute ────────────────────────────────────────────────────
    result = await db.execute(query)
    employees = result.scalars().all()

    # ── Step 5: Build rows ────────────────────────────────────────────────
    rows = []
    for emp in employees:
        rows.append({
            "id": str(emp.id),
            "employee_id": emp.employee_id or "—",
            "employee_name": emp.employee_name or "—",
            "designation_id": str(emp.designation_id) if emp.designation_id else "—",
            "department_id": str(emp.department_id) if emp.department_id else "—",
            "status": emp.status or "Active",
        })

    # ── Step 6: Build UIResponse ──────────────────────────────────────────
    response_context = context_for_module(user.tenant_id, "hrms")

    actions = []
    if check_permission(user, "hrms", "create"):
        actions.append(UIAction(
            action_id="add_employee",
            label="Add Employee",
            style="primary",
            endpoint="/api/employees/",
            method="POST",
            payload={},
            confirmation_required=False,
        ))

    status_label = status_filter.lower() if status_filter else "all"
    return make_table_response(
        message=f"Here are the {status_label} employees ({len(rows)} total):",
        context=response_context,
        columns=["employee_id", "employee_name", "designation_id", "department_id", "status"],
        column_labels={
            "employee_id": "Employee ID",
            "employee_name": "Name",
            "designation_id": "Designation",
            "department_id": "Department",
            "status": "Status",
        },
        rows=rows,
        total=len(rows),
        record_type="employee",
        row_id_field="id",
        actions=actions,
    )
```

---

## 9. HR Agent Node

File: `backend/app/veda/agents/hr_agent.py`

```python
from app.db.database import AsyncSessionLocal
from app.veda.state import AgentState
from app.veda.tools.hr_tools import list_employees_tool
from app.schemas.ui_response import make_blocker_response


# Tool registry — add new tools here as Phase 3.2 progresses
HR_TOOLS = {
    "list_employees": list_employees_tool,
    # Phase 3.2:
    # "get_employee": get_employee_tool,
    # "list_leave_applications": list_leave_applications_tool,
    # "approve_leave": approve_leave_tool,
}


async def hr_agent_node(state: AgentState) -> AgentState:
    """
    HR Agent node. Looks up and executes the correct HR tool.

    Reads from state:
        tool_name:   which tool to execute (set by supervisor)
        tool_params: parameters for the tool (set by supervisor)
        user:        authenticated user
        context:     active UI context

    Writes to state:
        response:    UIResponse from the tool (or BLOCKER on error)
    """
    tool_name = state.get("tool_name")
    tool_params = state.get("tool_params") or {}
    user = state["user"]
    context = state["context"]

    tool_fn = HR_TOOLS.get(tool_name)

    if tool_fn is None:
        response = make_blocker_response(
            reason=f"I don't know how to handle '{tool_name}' yet. This capability is coming soon.",
            resolution_options=[],
            context=context,
            blocked_task=str(tool_name),
        )
        return {**state, "response": response}

    async with AsyncSessionLocal() as db:
        try:
            response = await tool_fn(
                db=db,
                user=user,
                context=context,
                **tool_params,
            )
        except Exception as e:
            await db.rollback()
            response = make_blocker_response(
                reason="An error occurred while processing your request. Please try again.",
                resolution_options=[],
                context=context,
                blocked_task=str(tool_name),
            )

    return {**state, "response": response}
```

---

## 10. Endpoint Integration

Replace the existing stub in `backend/app/main.py` with this:

```python
# Add these imports at the top of main.py
from app.veda.state import build_initial_state
from app.veda.graph import veda_graph
from app.schemas.user_context import UserContext

# Replace the existing /api/veda/chat stub with this:
@app.post("/api/veda/chat", response_model=UIResponse)
async def veda_chat(
    request: VEDARequest,
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: UserContext = Depends(get_current_user),
):
    """
    VEDA chat endpoint. Processes natural language, returns UIResponse.

    Flow:
    1. Sanitise context  — JWT tenant_id overwrites any client-supplied value
    2. Build graph state — assemble initial AgentState
    3. Invoke graph      — supervisor routes → agent executes → UIResponse set
    4. Return response   — always a typed UIResponse, never plain text
    """
    safe_context = sanitise_request_context(request.context, tenant_id)

    initial_state = build_initial_state(
        message=request.message,
        context=safe_context,
        user=current_user,
        conversation_history=request.conversation_history,
    )

    try:
        final_state = await veda_graph.ainvoke(initial_state)
    except Exception as e:
        return make_text_response(
            message="I encountered an error processing your request. Please try again.",
            context=safe_context,
            hints=["Show all employees", "Help"],
        )

    if final_state.get("response"):
        return final_state["response"]

    # Fallback — should not be reached if supervisor is implemented correctly
    return make_text_response(
        message="I'm not sure how to help with that. Could you rephrase?",
        context=safe_context,
        hints=["Show all employees", "Help"],
    )
```

---

## 11. Conversation History Handling

Multi-turn conversations pass the last 10 messages as `conversation_history`.
This is already handled in `classify_intent()` in supervisor.py (Section 7).
The `build_initial_state()` factory enforces the 10-message cap via `[-10:]`.

Message format expected in `conversation_history`:
```python
[
    {"role": "user",      "content": "Show me all employees"},
    {"role": "assistant", "content": "Here are the active employees (22 total): ..."},
    {"role": "user",      "content": "Filter to just the engineering department"},
]
```

---

## 12. Testing Pattern

File: `backend/app/tests/test_veda_task31.py`

```python
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app.veda.state import build_initial_state
from app.veda.tools.hr_tools import list_employees_tool
from app.schemas.user_context import UserContext
from app.schemas.ui_response import UIResponseType
from app.utils.veda_context import null_context


def make_user(role: str, tenant_id=None) -> UserContext:
    tid = tenant_id or uuid4()
    return UserContext(
        user_id=uuid4(),
        tenant_id=tid,
        role=role,
        employee_id=uuid4(),
        company_id=uuid4(),
    )


class TestListEmployeesTool:

    @pytest.mark.asyncio
    async def test_owner_gets_table_response(self, db_session):
        user = make_user("owner")
        context = null_context(user.tenant_id)
        response = await list_employees_tool(db_session, user, context)
        assert response.type == UIResponseType.TABLE

    @pytest.mark.asyncio
    async def test_finance_manager_gets_blocker(self, db_session):
        user = make_user("finance_manager")
        context = null_context(user.tenant_id)
        response = await list_employees_tool(db_session, user, context)
        assert response.type == UIResponseType.BLOCKER
        assert "does not have access" in response.payload.reason

    @pytest.mark.asyncio
    async def test_table_response_has_required_fields(self, db_session):
        user = make_user("owner")
        context = null_context(user.tenant_id)
        response = await list_employees_tool(db_session, user, context)
        assert response.payload.columns is not None
        assert response.payload.record_type == "employee"
        assert response.payload.row_id_field == "id"

    @pytest.mark.asyncio
    async def test_manager_sees_only_team(self, db_session):
        """Manager should only see employees in their reporting chain."""
        user = make_user("manager")
        context = null_context(user.tenant_id)
        response = await list_employees_tool(db_session, user, context)
        # Either TABLE (if they have reports) or BLOCKER (if no reports set up)
        assert response.type in (UIResponseType.TABLE, UIResponseType.BLOCKER)
```

---

## 13. Environment Variable Required

The ANTHROPIC_API_KEY must be set in the environment before starting the server.
Add to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Load in `backend/app/main.py` or `backend/app/db/database.py` using:
```python
from dotenv import load_dotenv
load_dotenv()
```

If `python-dotenv` is not in `requirements.txt`, add it.

---

## 14. Gate Checklist for Task 3.1

All 5 gates must pass before marking Task 3.1 complete.

| Gate | How to Test |
|------|-------------|
| Gate 1 | `POST /api/veda/chat` body: `{"message": "Show me all active employees", "context": {...}, "conversation_history": []}` with owner JWT → response `type` field equals `"table"` |
| Gate 2 | Same response → `payload.columns` exists, `payload.record_type == "employee"`, `payload.rows` is an array |
| Gate 3 | Read `backend/app/veda/supervisor.py` — confirm `describe_user(user)` and `describe_context(context)` are both called inside `supervisor_node` and passed to `classify_intent` |
| Gate 4 | Owner JWT → `payload.total` equals the actual employee count in the database (verify against `GET /api/employees/`) |
| Gate 5 | Manager JWT → `payload.rows` count is less than or equal to owner's count (org scope applied) |