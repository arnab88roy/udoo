from uuid import UUID
from fastapi import HTTPException
from app.schemas.user_context import UserContext

DEFAULT_PERMISSIONS = {
    "owner": {
        "hrms":     {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": True},
        "payroll":  {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": True},
        "finance":  {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": True},
        "settings": {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": True},
        "crm":      {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": True},
        "tasks":    {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": True},
    },
    "hr_manager": {
        "hrms":     {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": True},
        "payroll":  {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": False},
        "finance":  {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "settings": {"view": True,  "create": False, "edit": True,  "submit": False, "approve": False, "delete": False},
        "crm":      {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "tasks":    {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": False},
    },
    "finance_manager": {
        "hrms":     {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "payroll":  {"view": True,  "create": False, "edit": False, "submit": False, "approve": True,  "delete": False},
        "finance":  {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": True},
        "settings": {"view": True,  "create": False, "edit": True,  "submit": False, "approve": False, "delete": False},
        "crm":      {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": False},
        "tasks":    {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": False},
    },
    "manager": {
        "hrms":     {"view": True,  "create": False, "edit": False, "submit": False, "approve": True,  "delete": False},
        "payroll":  {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "finance":  {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "settings": {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "crm":      {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": False, "delete": False},
        "tasks":    {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": True,  "delete": False},
    },
    "employee": {
        "hrms":     {"view": True,  "create": False, "edit": False, "submit": True,  "approve": False, "delete": False},
        "payroll":  {"view": True,  "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "finance":  {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "settings": {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "crm":      {"view": False, "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "tasks":    {"view": True,  "create": True,  "edit": True,  "submit": True,  "approve": False, "delete": False},
    },
    "auditor": {
        "hrms":     {"view": True,  "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "payroll":  {"view": True,  "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "finance":  {"view": True,  "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "settings": {"view": True,  "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "crm":      {"view": True,  "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
        "tasks":    {"view": True,  "create": False, "edit": False, "submit": False, "approve": False, "delete": False},
    },
}


def check_permission(user: UserContext, module: str, action: str) -> bool:
    """Check if a user has permission. Returns True/False."""
    role_perms = DEFAULT_PERMISSIONS.get(user.role, {})
    module_perms = role_perms.get(module, {})
    return module_perms.get(action, False)


def require_permission(user: UserContext, module: str, action: str) -> None:
    """Assert permission. Raises HTTP 403 if not permitted."""
    if not check_permission(user, module, action):
        raise HTTPException(
            status_code=403,
            detail=f"You do not have permission to {action} in {module}. "
                   f"Your role ({user.role}) does not allow this action."
        )


def require_own_record(user: UserContext, record_employee_id: UUID) -> None:
    """
    Assert employee is accessing their own record.
    Owner, HR Manager, and Auditor bypass this check.
    """
    if user.role in ("owner", "hr_manager", "auditor"):
        return
    if user.employee_id != record_employee_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own records."
        )
