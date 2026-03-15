from app.db.database import AsyncSessionLocal
from app.veda.state import AgentState
from app.veda.tools.hr_tools import (
    list_employees_tool,
    get_employee_tool,
    list_leave_applications_tool,
    approve_leave_tool,
    get_attendance_summary_tool,
    get_my_permissions_tool,
)
from app.schemas.ui_response import make_blocker_response


# Tool registry — add new tools here as Phase 3.2 progresses
HR_TOOLS = {
    "list_employees": list_employees_tool,
    "get_employee": get_employee_tool,
    "list_leave_applications": list_leave_applications_tool,
    "approve_leave": approve_leave_tool,
    "get_attendance_summary": get_attendance_summary_tool,
    "get_my_permissions": get_my_permissions_tool,
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
