from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.dependencies import get_tenant_id
from app.modules.hr_masters import models, schemas

leave_type_router = APIRouter(prefix="/leave-types", tags=["Leave Types"])

@leave_type_router.post("/", response_model=schemas.LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_type(entity: schemas.LeaveTypeCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    db_obj = models.LeaveType(**entity.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@leave_type_router.get("/", response_model=List[schemas.LeaveTypeResponse])
async def list_leave_types(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.LeaveType).where(models.LeaveType.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@leave_type_router.get("/{id}", response_model=schemas.LeaveTypeResponse)
async def get_leave_type(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.LeaveType).where(models.LeaveType.id == id, models.LeaveType.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Leave Type not found")
    return obj


leave_application_router = APIRouter(prefix="/leave-applications", tags=["Leave Applications"])

@leave_application_router.post("/", response_model=schemas.LeaveApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_application(entity: schemas.LeaveApplicationCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    db_obj = models.LeaveApplication(**entity.model_dump(), tenant_id=tenant_id)
    # Status should start as Draft (0) by default in schema (0)
    db_obj.docstatus = 0
    db_obj.status = "Open"
    
    db.add(db_obj)
    await db.commit()
    
    # Eager load relationships for response
    stmt = (
        select(models.LeaveApplication)
        .options(
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.education),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.external_work_history),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.internal_work_history),
            selectinload(models.LeaveApplication.leave_type)
        )
        .where(models.LeaveApplication.id == db_obj.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()

@leave_application_router.get("/", response_model=List[schemas.LeaveApplicationResponse])
async def list_leave_applications(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = (
        select(models.LeaveApplication)
        .options(
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.education),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.external_work_history),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.internal_work_history),
            selectinload(models.LeaveApplication.leave_type)
        )
        .where(models.LeaveApplication.tenant_id == tenant_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@leave_application_router.get("/{id}", response_model=schemas.LeaveApplicationResponse)
async def get_leave_application(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = (
        select(models.LeaveApplication)
        .options(
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.education),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.external_work_history),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.internal_work_history),
            selectinload(models.LeaveApplication.leave_type)
        )
        .where(models.LeaveApplication.id == id, models.LeaveApplication.tenant_id == tenant_id)
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Leave Application not found")
    return obj

# --- State Machine Endpoints ---

@leave_application_router.post("/{id}/submit", response_model=schemas.LeaveApplicationResponse)
async def submit_leave_application(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.LeaveApplication).where(models.LeaveApplication.id == id, models.LeaveApplication.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Leave Application not found")
    
    if obj.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only Draft applications can be submitted.")
        
    obj.docstatus = 1
    await db.commit()
    
    # Eager load for response
    refresh_stmt = (
        select(models.LeaveApplication)
        .options(
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.education),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.external_work_history),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.internal_work_history),
            selectinload(models.LeaveApplication.leave_type)
        )
        .where(models.LeaveApplication.id == obj.id)
    )
    result = await db.execute(refresh_stmt)
    return result.scalar_one()

@leave_application_router.post("/{id}/approve", response_model=schemas.LeaveApplicationResponse)
async def approve_leave_application(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.LeaveApplication).where(models.LeaveApplication.id == id, models.LeaveApplication.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Leave Application not found")
    
    if obj.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted applications can be approved.")
        
    obj.status = "Approved"
    await db.commit()
    
    # Eager load
    refresh_stmt = (
        select(models.LeaveApplication)
        .options(
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.education),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.external_work_history),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.internal_work_history),
            selectinload(models.LeaveApplication.leave_type)
        )
        .where(models.LeaveApplication.id == obj.id)
    )
    result = await db.execute(refresh_stmt)
    return result.scalar_one()

@leave_application_router.post("/{id}/cancel", response_model=schemas.LeaveApplicationResponse)
async def cancel_leave_application(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.LeaveApplication).where(models.LeaveApplication.id == id, models.LeaveApplication.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Leave Application not found")
    
    if obj.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted applications can be cancelled.")
        
    obj.docstatus = 2
    await db.commit()
    
    # Eager load for response
    refresh_stmt = (
        select(models.LeaveApplication)
        .options(
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.education),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.external_work_history),
            selectinload(models.LeaveApplication.employee).selectinload(models.Employee.internal_work_history),
            selectinload(models.LeaveApplication.leave_type)
        )
        .where(models.LeaveApplication.id == obj.id, models.LeaveApplication.tenant_id == tenant_id)
    )
    result = await db.execute(refresh_stmt)
    return result.scalar_one()
