from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def get_subordinate_ids(
    db: AsyncSession,
    manager_employee_id: UUID,
    tenant_id: UUID,
    include_self: bool = True,
) -> List[UUID]:
    """
    Returns all employee IDs under a manager using a recursive CTE.
    Traverses the full org hierarchy via reports_to_id.
    """
    query = text("""
        WITH RECURSIVE subordinates AS (
            SELECT id
            FROM hr_employees
            WHERE id = :manager_id
              AND tenant_id = :tenant_id

            UNION ALL

            SELECT e.id
            FROM hr_employees e
            INNER JOIN subordinates s ON e.reports_to_id = s.id
            WHERE e.tenant_id = :tenant_id
        )
        SELECT id FROM subordinates
        WHERE (:include_self = TRUE OR id != :manager_id)
    """)

    result = await db.execute(query, {
        "manager_id": str(manager_employee_id),
        "tenant_id": str(tenant_id),
        "include_self": include_self,
    })

    return [row[0] for row in result.fetchall()]


async def get_visible_employee_ids(
    db: AsyncSession,
    user,  # UserContext — avoid circular import by not typing here
    tenant_id: UUID,
) -> Optional[List[UUID]]:
    """
    Returns employee IDs visible to this user based on their role.
    Returns None = no filter (user sees all employees).
    Returns [] = sees nothing.
    Returns [list] = scoped to these IDs only.

    Scope rules:
      owner / hr_manager / auditor  → None (sees all)
      finance_manager               → [] (no employee visibility)
      manager                       → recursive subordinates
      employee                      → [own employee_id only]
    """
    if user.role in ("owner", "hr_manager", "auditor"):
        return None

    if user.role == "manager":
        if not user.employee_id:
            return []
        return await get_subordinate_ids(
            db, user.employee_id, tenant_id, include_self=True
        )

    if user.role == "employee":
        if not user.employee_id:
            return []
        return [user.employee_id]

    return []
