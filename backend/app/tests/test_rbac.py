import pytest
from uuid import uuid4
from fastapi import HTTPException
from app.schemas.user_context import UserContext
from app.utils.permissions import check_permission, require_permission, require_own_record

def test_user_context_property_helpers():
    """Test UserContext role property helpers."""
    ctx = UserContext(user_id=uuid4(), tenant_id=uuid4(), role="hr_manager", employee_id=uuid4(), company_id=uuid4())
    assert ctx.is_hr_manager is True
    assert ctx.is_owner is False
    assert ctx.can_see_all_employees is True

def test_permission_matrix_owner():
    """Owner should have all permissions."""
    ctx = UserContext(user_id=uuid4(), tenant_id=uuid4(), role="owner", employee_id=None, company_id=uuid4())
    assert check_permission(ctx, "payroll", "view") is True
    assert check_permission(ctx, "settings", "delete") is True

def test_permission_matrix_employee():
    """Employee should have limited permissions."""
    ctx = UserContext(user_id=uuid4(), tenant_id=uuid4(), role="employee", employee_id=uuid4(), company_id=uuid4())
    assert check_permission(ctx, "payroll", "view") is True
    assert check_permission(ctx, "payroll", "submit") is False
    assert check_permission(ctx, "finance", "view") is False

def test_require_permission_raises_403():
    """require_permission should raise 403 on failure."""
    ctx = UserContext(user_id=uuid4(), tenant_id=uuid4(), role="employee", employee_id=uuid4(), company_id=uuid4())
    with pytest.raises(HTTPException) as excinfo:
        require_permission(ctx, "payroll", "submit")
    assert excinfo.value.status_code == 403

def test_require_own_record_success():
    """Employee can access their own record."""
    emp_id = uuid4()
    ctx = UserContext(user_id=uuid4(), tenant_id=uuid4(), role="employee", employee_id=emp_id, company_id=uuid4())
    # Should not raise
    require_own_record(ctx, emp_id)

def test_require_own_record_failure():
    """Employee cannot access another's record."""
    emp_id = uuid4()
    other_id = uuid4()
    ctx = UserContext(user_id=uuid4(), tenant_id=uuid4(), role="employee", employee_id=emp_id, company_id=uuid4())
    with pytest.raises(HTTPException) as excinfo:
        require_own_record(ctx, other_id)
    assert excinfo.value.status_code == 403

def test_require_own_record_bypass_owner():
    """Owner bypasses own record check."""
    ctx = UserContext(user_id=uuid4(), tenant_id=uuid4(), role="owner", employee_id=None, company_id=uuid4())
    # Should not raise even if IDs differ
    require_own_record(ctx, uuid4())

def test_require_own_record_bypass_hr():
    """HR Manager bypasses own record check."""
    ctx = UserContext(user_id=uuid4(), tenant_id=uuid4(), role="hr_manager", employee_id=uuid4(), company_id=uuid4())
    # Should not raise even if IDs differ
    require_own_record(ctx, uuid4())

def test_hr_manager_no_finance_access():
    """
    HR Manager must have ZERO access to the finance module.
    This is a critical boundary — HR should never see client data,
    invoices, or financial records.
    """
    ctx = UserContext(
        user_id=uuid4(), tenant_id=uuid4(),
        role="hr_manager", employee_id=uuid4(), company_id=uuid4()
    )
    assert check_permission(ctx, "hrms", "approve") is True    # has hrms
    assert check_permission(ctx, "payroll", "submit") is True  # has payroll
    assert check_permission(ctx, "finance", "view") is False   # no finance
    assert check_permission(ctx, "finance", "create") is False
    assert check_permission(ctx, "finance", "approve") is False


def test_finance_manager_no_hrms_access():
    """
    Finance Manager must have ZERO access to the HRMS module.
    This is a critical boundary — Finance should never see employee
    personal data, salaries, or leave records.
    """
    ctx = UserContext(
        user_id=uuid4(), tenant_id=uuid4(),
        role="finance_manager", employee_id=uuid4(), company_id=uuid4()
    )
    assert check_permission(ctx, "finance", "approve") is True  # has finance
    assert check_permission(ctx, "crm", "create") is True       # has crm
    assert check_permission(ctx, "hrms", "view") is False       # no hrms
    assert check_permission(ctx, "hrms", "create") is False
    assert check_permission(ctx, "hrms", "approve") is False


def test_manager_view_approve_only_no_create_or_payroll():
    """
    Manager can view and approve HRMS records for their team
    but cannot create records or access payroll at all.
    This enforces the team lead role — decision maker, not admin.
    """
    ctx = UserContext(
        user_id=uuid4(), tenant_id=uuid4(),
        role="manager", employee_id=uuid4(), company_id=uuid4()
    )
    assert check_permission(ctx, "hrms", "view") is True      # can view
    assert check_permission(ctx, "hrms", "approve") is True   # can approve
    assert check_permission(ctx, "hrms", "create") is False   # cannot create
    assert check_permission(ctx, "hrms", "edit") is False     # cannot edit
    assert check_permission(ctx, "payroll", "view") is False  # no payroll
    assert check_permission(ctx, "payroll", "submit") is False
    assert check_permission(ctx, "finance", "view") is False  # no finance


def test_auditor_read_only_all_modules():
    """
    Auditor can VIEW everything across all modules
    but cannot create, edit, submit, approve, or delete anything.
    This enforces the read-only audit access pattern.
    """
    ctx = UserContext(
        user_id=uuid4(), tenant_id=uuid4(),
        role="auditor", employee_id=uuid4(), company_id=uuid4()
    )
    # Can view all modules
    for module in ["hrms", "payroll", "finance", "settings", "crm", "tasks"]:
        assert check_permission(ctx, module, "view") is True, \
            f"Auditor should be able to view {module}"

    # Cannot modify anything in any module
    for module in ["hrms", "payroll", "finance", "settings", "crm", "tasks"]:
        assert check_permission(ctx, module, "create") is False, \
            f"Auditor should NOT be able to create in {module}"
        assert check_permission(ctx, module, "approve") is False, \
            f"Auditor should NOT be able to approve in {module}"
        assert check_permission(ctx, module, "delete") is False, \
            f"Auditor should NOT be able to delete in {module}"
