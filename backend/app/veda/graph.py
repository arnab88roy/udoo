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
