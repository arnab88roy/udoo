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
- "approve_leave"          — user wants to approve a leave request (or "open approval card")
- "get_attendance_summary" — user wants a summary of attendance (e.g. "attendance last 7 days")
- "get_my_permissions"     — user wants to know what they can do (e.g. "what are my permissions?")

For agent "payroll", identify the tool:
- "get_payroll_status"     — user wants to know the overview of payroll for a month (e.g. "payroll status", "did everyone get payslips?")
- "run_payroll_bulk"       — user wants to generate salary slips for the month (e.g. "run payroll", "generate slips")
- "get_salary_slip"        — user wants to see their own or someone's payslip (e.g. "my payslip", "show payslip for Jan")

Extract any parameters mentioned:
- For list_employees:          {{ "status_filter": "Active" }} (default Active, or "all" / "Inactive")
- For get_employee:            {{ "name": "Dev Patel" }} or {{ "employee_id": "EMP-001" }}
- For list_leave_applications: {{ "status": "Open" }} (default Open, or "Approved" / "Rejected" / "all")
- For approve_leave:           {{ "leave_id": "uuid-here" }} if mentioned
- For get_attendance_summary:  {{ "days": 7 }} (default 7, or as mentioned)
- For get_payroll_status:      {{ "month": 3, "year": 2024 }} (extract numeric month/year)
- For run_payroll_bulk: {{ "month": 3, "year": 2026, "working_days": 26 }} (extract numeric month/year if mentioned)
- For get_salary_slip:         {{ "name": "Dev Patel", "month": 3, "year": 2024 }}

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

    # ── Block unimplemented agents (finance, setup) ───────────────
    # Remove this block when the corresponding agent is implemented.
    if agent in ("finance", "setup"):
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
