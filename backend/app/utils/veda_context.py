from uuid import UUID
from typing import Optional
from app.schemas.ui_response import UIContext


def build_context(
    tenant_id: UUID,
    open_record_type: Optional[str] = None,
    open_record_id: Optional[UUID] = None,
    open_module: Optional[str] = None,
) -> UIContext:
    """
    Build a UIContext object with the server-authoritative tenant_id.
    Always use this function when constructing context server-side.
    Never trust tenant_id values supplied by the client.

    Args:
        tenant_id: Always sourced from the decoded JWT. Non-negotiable.
        open_record_type: The entity type open in the editor, if any.
        open_record_id: The UUID of the open record, if any.
        open_module: The active module (hrms, payroll, finance, settings), if any.

    Returns:
        UIContext with server-authoritative tenant_id.
    """
    return UIContext(
        tenant_id=tenant_id,
        open_record_type=open_record_type,
        open_record_id=open_record_id,
        open_module=open_module,
    )


def null_context(tenant_id: UUID) -> UIContext:
    """
    Constructs a UIContext with no active record.
    Use this when the backend generates a UIResponse that is NOT
    in direct response to a user message — for example:
    - Background task completion notifications
    - Scheduled payroll reminders
    - System-initiated approval requests

    Without this helper, background tasks must manually construct
    UIContext(tenant_id=x, open_record_type=None, ...) which is
    verbose and easy to get wrong.

    Args:
        tenant_id: The tenant this response belongs to.
                   Always source from JWT or the task's tenant scope.

    Returns:
        UIContext with all record fields set to None.

    Example:
        # In a background payroll task:
        context = null_context(tenant_id=tenant_id)
        response = make_progress_response("Payroll running...", steps, context)
    """
    return UIContext(
        tenant_id=tenant_id,
        open_record_type=None,
        open_record_id=None,
        open_module=None,
    )


def context_for_module(tenant_id: UUID, module: str) -> UIContext:
    """
    Constructs a UIContext scoped to a module but with no specific record open.
    Use this when VEDA is operating within a module context
    (e.g. after routing to the payroll agent) but hasn't opened
    a specific record yet.

    Args:
        tenant_id: Always from JWT.
        module: One of 'hrms', 'payroll', 'finance', 'settings'.

    Returns:
        UIContext with open_module set, record fields None.

    Example:
        # HR agent responding to "show pending leaves":
        context = context_for_module(tenant_id, 'hrms')
        response = make_table_response("Pending leaves:", context, ...)
    """
    return UIContext(
        tenant_id=tenant_id,
        open_record_type=None,
        open_record_id=None,
        open_module=module,
    )


def context_for_record(
    tenant_id: UUID,
    record_type: str,
    record_id: UUID,
    module: str,
) -> UIContext:
    """
    Constructs a UIContext with a specific record open.
    Use this when VEDA has identified the specific record it is
    operating on — for example after fetching an employee by name,
    or after the user clicks a row in an inline table.

    Args:
        tenant_id: Always from JWT.
        record_type: Entity type. e.g. 'employee', 'leave_application'.
        record_id: UUID of the specific record.
        module: The module this record belongs to.

    Returns:
        Fully populated UIContext.

    Example:
        # After fetching employee by name match:
        context = context_for_record(tenant_id, 'employee', emp.id, 'hrms')
        response = make_form_response("Here is Priya's record:", ..., context)
    """
    return UIContext(
        tenant_id=tenant_id,
        open_record_type=record_type,
        open_record_id=record_id,
        open_module=module,
    )


def sanitise_request_context(
    request_context: UIContext,
    jwt_tenant_id: UUID,
) -> UIContext:
    """
    Takes the UIContext sent by the client and overwrites tenant_id
    with the value from the JWT. All other context fields are
    passed through as-is (they are UI state, not security-sensitive).

    This is the single authoritative function for context sanitisation.
    Call this at the top of every VEDA endpoint handler.

    Args:
        request_context: The UIContext from the client request body.
        jwt_tenant_id: The tenant_id decoded from the JWT by get_tenant_id().

    Returns:
        A sanitised UIContext with JWT tenant_id enforced.
    """
    return UIContext(
        tenant_id=jwt_tenant_id,                           # JWT always wins
        open_record_type=request_context.open_record_type,
        open_record_id=request_context.open_record_id,
        open_module=request_context.open_module,
    )


def is_record_context_active(context: UIContext) -> bool:
    """
    Returns True if the user currently has a specific record open.
    Used by LangGraph agents to decide whether to scope queries.

    Example:
        if is_record_context_active(context):
            # query is scoped to context.open_record_id
        else:
            # ask the user which record they mean
    """
    return (
        context.open_record_type is not None
        and context.open_record_id is not None
    )


def context_matches_type(context: UIContext, expected_type: str) -> bool:
    """
    Returns True if the active record context matches the expected type.
    Use this in LangGraph agent nodes as a guard before assuming
    the open record is a specific entity type.

    This prevents a common agent error: the user is on an employee record,
    switches to a leave application, and the HR agent still tries to
    operate on the employee because it cached the old context.

    Args:
        context: The current UIContext from the request.
        expected_type: The entity type the agent expects.
                       e.g. 'employee', 'leave_application'.

    Returns:
        True only if both open_record_type matches AND open_record_id is set.

    Example:
        # In HR agent, before using context as employee:
        if context_matches_type(context, 'employee'):
            employee = await fetch_employee(context.open_record_id)
        else:
            # Ask user or search by name
    """
    return (
        is_record_context_active(context)
        and context.open_record_type == expected_type
    )


def describe_context(context: UIContext) -> str:
    """
    Returns a human-readable description of the active context.
    Injected into LangGraph agent system prompts to give VEDA
    awareness of what the user is currently looking at.

    Example output:
        "The user currently has a employee record (ID: abc123) open
         in the hrms module. Queries should be scoped to this record
         unless the user specifies otherwise."

        "The user is in the payroll module but no specific record is open."

        "No record is currently open. The user is on the home dashboard.
         Ask for clarification before operating on any specific record."
    """
    if is_record_context_active(context):
        module_str = f" in the {context.open_module} module" if context.open_module else ""
        return (
            f"The user currently has a {context.open_record_type} record "
            f"(ID: {context.open_record_id}) open{module_str}. "
            f"Queries should be scoped to this record unless the user specifies otherwise."
        )
    elif context.open_module:
        return (
            f"The user is in the {context.open_module} module "
            f"but no specific record is open."
        )
    else:
        return (
            "No record is currently open. "
            "The user is on the home dashboard. "
            "Ask for clarification before operating on any specific record."
        )
