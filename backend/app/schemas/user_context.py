from dataclasses import dataclass
from uuid import UUID
from typing import Optional

@dataclass
class UserContext:
    """
    Typed representation of the authenticated user extracted from JWT.
    Passed via Depends(get_current_user) into every protected endpoint.

    This is NOT a database model. It is derived from the JWT at request time.
    Never cache this object between requests.
    """
    user_id: UUID
    tenant_id: UUID
    role: str
    employee_id: Optional[UUID]
    company_id: Optional[UUID]

    @property
    def is_owner(self) -> bool:
        return self.role == "owner"

    @property
    def is_hr_manager(self) -> bool:
        return self.role == "hr_manager"

    @property
    def is_finance_manager(self) -> bool:
        return self.role == "finance_manager"

    @property
    def is_manager(self) -> bool:
        return self.role == "manager"

    @property
    def is_employee(self) -> bool:
        return self.role == "employee"

    @property
    def is_auditor(self) -> bool:
        return self.role == "auditor"

    @property
    def can_see_all_employees(self) -> bool:
        """
        Owner, HR Manager, and Auditor can see all employees.
        Manager sees their team only.
        Employee sees themselves only.
        Finance Manager sees no employee personal data.
        """
        return self.role in ("owner", "hr_manager", "auditor")

    @property
    def has_payroll_access(self) -> bool:
        return self.role in ("owner", "hr_manager")

    @property
    def has_finance_access(self) -> bool:
        return self.role in ("owner", "finance_manager")
