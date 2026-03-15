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
