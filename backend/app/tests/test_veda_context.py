import pytest
import uuid
from app.schemas.ui_response import UIContext
from app.utils.veda_context import (
    build_context,
    null_context,
    context_for_module,
    context_for_record,
    sanitise_request_context,
    is_record_context_active,
    context_matches_type,
    describe_context,
)


# ===== UNIT TESTS =====

def test_build_context_sets_tenant_id():
    tid = uuid.uuid4()
    ctx = build_context(tenant_id=tid, open_module="hrms")
    assert ctx.tenant_id == tid
    assert ctx.open_module == "hrms"
    assert ctx.open_record_type is None
    assert ctx.open_record_id is None


def test_sanitise_overwrites_client_tenant_id():
    """
    SECURITY TEST: Client cannot spoof tenant_id through context body.
    The JWT tenant_id must always win.
    """
    client_tenant = uuid.uuid4()
    jwt_tenant = uuid.uuid4()
    assert client_tenant != jwt_tenant

    client_context = UIContext(
        tenant_id=client_tenant,
        open_record_type="employee",
        open_record_id=uuid.uuid4(),
        open_module="hrms"
    )

    safe = sanitise_request_context(client_context, jwt_tenant)

    assert safe.tenant_id == jwt_tenant          # JWT must win
    assert safe.tenant_id != client_tenant       # client value must be gone
    assert safe.open_record_type == "employee"   # non-security fields pass through
    assert safe.open_module == "hrms"


def test_is_record_context_active_true():
    ctx = UIContext(
        tenant_id=uuid.uuid4(),
        open_record_type="leave_application",
        open_record_id=uuid.uuid4(),
        open_module="hrms"
    )
    assert is_record_context_active(ctx) is True


def test_is_record_context_active_false_when_no_record():
    ctx = UIContext(
        tenant_id=uuid.uuid4(),
        open_record_type=None,
        open_record_id=None,
        open_module="hrms"
    )
    assert is_record_context_active(ctx) is False


def test_describe_context_with_open_record():
    record_id = uuid.uuid4()
    ctx = UIContext(
        tenant_id=uuid.uuid4(),
        open_record_type="employee",
        open_record_id=record_id,
        open_module="hrms"
    )
    description = describe_context(ctx)
    assert "employee" in description
    assert str(record_id) in description
    assert "hrms" in description


def test_null_context_has_no_record():
    tid = uuid.uuid4()
    ctx = null_context(tid)
    assert ctx.tenant_id == tid
    assert ctx.open_record_type is None
    assert ctx.open_record_id is None
    assert ctx.open_module is None
    assert is_record_context_active(ctx) is False


def test_context_for_module_has_no_record():
    ctx = context_for_module(uuid.uuid4(), "payroll")
    assert ctx.open_module == "payroll"
    assert ctx.open_record_id is None
    assert is_record_context_active(ctx) is False


def test_context_for_record_is_fully_populated():
    tid = uuid.uuid4()
    rid = uuid.uuid4()
    ctx = context_for_record(tid, "employee", rid, "hrms")
    assert ctx.tenant_id == tid
    assert ctx.open_record_type == "employee"
    assert ctx.open_record_id == rid
    assert ctx.open_module == "hrms"
    assert is_record_context_active(ctx) is True


def test_context_matches_type_guard():
    ctx = context_for_record(
        uuid.uuid4(), "leave_application", uuid.uuid4(), "hrms"
    )
    assert context_matches_type(ctx, "leave_application") is True
    assert context_matches_type(ctx, "employee") is False
    assert context_matches_type(ctx, "salary_slip") is False
