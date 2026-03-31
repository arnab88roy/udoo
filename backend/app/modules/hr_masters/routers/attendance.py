from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.dependencies import get_tenant_id, get_current_user
from app.schemas.user_context import UserContext
from app.utils.permissions import require_permission
from app.utils.org_scope import get_visible_employee_ids
from app.modules.hr_masters import models, schemas

checkin_router = APIRouter(prefix="/employee-checkins", tags=["Employee Checkins"])

@checkin_router.post("/", response_model=schemas.EmployeeCheckinResponse, status_code=status.HTTP_201_CREATED)
async def create_employee_checkin(data: schemas.EmployeeCheckinCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "create")
    db_obj = models.EmployeeCheckin(**data.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    await db.commit()
    
    stmt = select(models.EmployeeCheckin).options(selectinload(models.EmployeeCheckin.employee)).where(models.EmployeeCheckin.id == db_obj.id, models.EmployeeCheckin.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@checkin_router.get("/", response_model=List[schemas.EmployeeCheckinResponse])
async def list_employee_checkins(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user), skip: int = 0, limit: int = 100):
    require_permission(current_user, "hrms", "view")
    stmt = select(models.EmployeeCheckin).options(selectinload(models.EmployeeCheckin.employee)).where(models.EmployeeCheckin.tenant_id == tenant_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@checkin_router.get("/{id}", response_model=schemas.EmployeeCheckinResponse)
async def get_employee_checkin(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "view")
    stmt = select(models.EmployeeCheckin).options(selectinload(models.EmployeeCheckin.employee)).where(models.EmployeeCheckin.id == id, models.EmployeeCheckin.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Employee Checkin not found")
    return obj


attendance_router = APIRouter(prefix="/attendance", tags=["Attendance"])

@attendance_router.post("/", response_model=schemas.AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(data: schemas.AttendanceCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "create")
    # Check for duplicate: employee_id + attendance_date
    dup_stmt = select(models.Attendance).where(
        models.Attendance.employee_id == data.employee_id,
        models.Attendance.attendance_date == data.attendance_date,
        models.Attendance.tenant_id == tenant_id
    )
    dup_res = await db.execute(dup_stmt)
    if dup_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Attendance record already exists for this employee on this date.")
        
    db_obj = models.Attendance(**data.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
        
    stmt = select(models.Attendance).options(selectinload(models.Attendance.employee)).where(models.Attendance.id == db_obj.id, models.Attendance.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@attendance_router.get("/", response_model=List[schemas.AttendanceResponse])
async def list_attendance(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user), skip: int = 0, limit: int = 100):
    require_permission(current_user, "hrms", "view")
    visible_ids = await get_visible_employee_ids(db, current_user, tenant_id)
    stmt = select(models.Attendance).options(selectinload(models.Attendance.employee)).where(models.Attendance.tenant_id == tenant_id)
    if visible_ids is not None:
        stmt = stmt.where(models.Attendance.employee_id.in_(visible_ids))
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@attendance_router.get("/{id}", response_model=schemas.AttendanceResponse)
async def get_attendance(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "view")
    stmt = select(models.Attendance).options(selectinload(models.Attendance.employee)).where(models.Attendance.id == id, models.Attendance.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return obj

@attendance_router.post("/{id}/submit", response_model=schemas.AttendanceResponse)
async def submit_attendance(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "submit")
    stmt = select(models.Attendance).where(models.Attendance.id == id, models.Attendance.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    if obj.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only Draft records can be submitted.")
        
    obj.docstatus = 1
    await db.commit()
    
    stmt = select(models.Attendance).options(selectinload(models.Attendance.employee)).where(models.Attendance.id == obj.id, models.Attendance.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@attendance_router.post("/{id}/cancel", response_model=schemas.AttendanceResponse)
async def cancel_attendance(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "submit")
    stmt = select(models.Attendance).where(models.Attendance.id == id, models.Attendance.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    if obj.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted records can be cancelled.")
        
    obj.docstatus = 2
    await db.commit()
    
    stmt = select(models.Attendance).options(selectinload(models.Attendance.employee)).where(models.Attendance.id == obj.id, models.Attendance.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()


attendance_request_router = APIRouter(prefix="/attendance-requests", tags=["Attendance Requests"])

@attendance_request_router.post("/", response_model=schemas.AttendanceRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance_request(data: schemas.AttendanceRequestCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "submit")
    db_obj = models.AttendanceRequest(**data.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    await db.commit()
    
    stmt = select(models.AttendanceRequest).options(selectinload(models.AttendanceRequest.employee)).where(models.AttendanceRequest.id == db_obj.id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@attendance_request_router.get("/", response_model=List[schemas.AttendanceRequestResponse])
async def list_attendance_requests(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user), skip: int = 0, limit: int = 100):
    require_permission(current_user, "hrms", "view")
    visible_ids = await get_visible_employee_ids(db, current_user, tenant_id)
    stmt = select(models.AttendanceRequest).options(selectinload(models.AttendanceRequest.employee)).where(models.AttendanceRequest.tenant_id == tenant_id)
    if visible_ids is not None:
        stmt = stmt.where(models.AttendanceRequest.employee_id.in_(visible_ids))
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@attendance_request_router.get("/{id}", response_model=schemas.AttendanceRequestResponse)
async def get_attendance_request(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "view")
    stmt = select(models.AttendanceRequest).options(selectinload(models.AttendanceRequest.employee)).where(models.AttendanceRequest.id == id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance Request not found")
    return obj

@attendance_request_router.post("/{id}/submit", response_model=schemas.AttendanceRequestResponse)
async def submit_attendance_request(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "submit")
    stmt = select(models.AttendanceRequest).where(models.AttendanceRequest.id == id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance Request not found")

    if obj.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only Draft records can be submitted.")
        
    obj.docstatus = 1
    await db.commit()
    
    stmt = select(models.AttendanceRequest).options(selectinload(models.AttendanceRequest.employee)).where(models.AttendanceRequest.id == obj.id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@attendance_request_router.post("/{id}/approve", response_model=schemas.AttendanceRequestResponse)
async def approve_attendance_request(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "approve")
    stmt = select(models.AttendanceRequest).where(models.AttendanceRequest.id == id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance Request not found")

    if obj.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted records can be approved.")
        
    obj.status = "Approved"
    await db.commit()
    
    stmt = select(models.AttendanceRequest).options(selectinload(models.AttendanceRequest.employee)).where(models.AttendanceRequest.id == obj.id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@attendance_request_router.post("/{id}/reject", response_model=schemas.AttendanceRequestResponse)
async def reject_attendance_request(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "approve")
    stmt = select(models.AttendanceRequest).where(models.AttendanceRequest.id == id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance Request not found")

    if obj.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted records can be rejected.")
        
    obj.status = "Rejected"
    await db.commit()
    
    stmt = select(models.AttendanceRequest).options(selectinload(models.AttendanceRequest.employee)).where(models.AttendanceRequest.id == obj.id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@attendance_request_router.post("/{id}/cancel", response_model=schemas.AttendanceRequestResponse)
async def cancel_attendance_request(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "hrms", "submit")
    stmt = select(models.AttendanceRequest).where(models.AttendanceRequest.id == id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Attendance Request not found")

    if obj.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted records can be cancelled.")
        
    obj.docstatus = 2
    await db.commit()
    
    stmt = select(models.AttendanceRequest).options(selectinload(models.AttendanceRequest.employee)).where(models.AttendanceRequest.id == obj.id, models.AttendanceRequest.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()
