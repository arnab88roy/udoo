from app.veda.state import AgentState
from app.db.database import AsyncSessionLocal
from app.veda.tools.payroll_tools import (
    get_payroll_status_tool,
    run_payroll_bulk_tool,
    get_salary_slip_tool
)
from app.schemas.ui_response import make_blocker_response
import logging

logger = logging.getLogger(__name__)

# Registry of tools this agent can execute
PAYROLL_TOOLS = {
    "get_payroll_status": get_payroll_status_tool,
    "run_payroll_bulk": run_payroll_bulk_tool,
    "get_salary_slip": get_salary_slip_tool,
}

async def payroll_agent_node(state: AgentState) -> AgentState:
    """
    Agent node for Payroll module.
    Executes tools requested by the supervisor.
    """
    tool_name = state.get("tool_name")
    tool_params = state.get("tool_params", {})
    user = state["user"]
    context = state["context"]
    
    # 1. Verification: tool must exist
    tool_func = PAYROLL_TOOLS.get(tool_name)
    if not tool_func:
        response = make_blocker_response(
            reason=f"I don't know how to handle '{tool_name}' in the payroll module yet.",
            resolution_options=[],
            context=context,
            blocked_task=str(tool_name),
        )
        return {**state, "response": response}

    # 2. Execution
    async with AsyncSessionLocal() as db:
        try:
            response = await tool_func(
                db=db, 
                user=user, 
                context=context,
                **tool_params
            )
            return {**state, "response": response}
        except Exception as e:
            logger.exception(f"Error executing payroll tool {tool_name}")
            await db.rollback()
            response = make_blocker_response(
                reason=f"An error occurred while processing your request: {str(e)}",
                resolution_options=[],
                context=context,
                blocked_task=str(tool_name),
            )
            return {**state, "response": response}
