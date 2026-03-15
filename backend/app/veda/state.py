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
