from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.dependencies import get_tenant_id
from app.modules.hr_masters import models, schemas


router = APIRouter(prefix="/holiday-lists", tags=["Holiday Lists"])

@router.post("/", response_model=schemas.HolidayListResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday_list(
    entity: schemas.HolidayListCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    # Extract child documents
    entity_data = entity.model_dump()
    holidays_data = entity_data.pop("holidays", [])
    
    # Create parent
    db_obj = models.HolidayList(**entity_data, tenant_id=tenant_id)
    # Calculate total holidays based on children count
    db_obj.total_holidays = len(holidays_data)
    
    # Add children mapped to tenant_id
    for holiday_data in holidays_data:
        child = models.Holiday(**holiday_data, tenant_id=tenant_id)
        db_obj.holidays.append(child)
        
    db.add(db_obj)
    try:
        await db.commit()
        await db.refresh(db_obj)
        # Refresh to eager load children
        stmt = select(models.HolidayList).options(selectinload(models.HolidayList.holidays)).where(models.HolidayList.id == db_obj.id)
        result = await db.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.HolidayListResponse])
async def list_holiday_lists(
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    stmt = select(models.HolidayList).options(selectinload(models.HolidayList.holidays)).where(models.HolidayList.tenant_id == tenant_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{id}", response_model=schemas.HolidayListResponse)
async def get_holiday_list(
    id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(models.HolidayList).options(selectinload(models.HolidayList.holidays)).where(models.HolidayList.id == id, models.HolidayList.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=404, detail="Holiday List not found")
    return obj

# --- Employee Endpoints ---
employee_router = APIRouter(prefix="/employees", tags=["Employees"])

@employee_router.post("/", response_model=schemas.EmployeeResponse)
async def create_employee(data: schemas.EmployeeCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    # 1. Compute Full Name
    full_parts = [p for p in [data.first_name, data.middle_name, data.last_name] if p]
    computed_name = " ".join(full_parts)

    # 2. Extract Nested Children
    edu_data = data.education
    ext_work = data.external_work_history
    int_work = data.internal_work_history

    # 3. Create Root Employee
    emp_dict = data.model_dump(exclude={"education", "external_work_history", "internal_work_history"})
    employee = models.Employee(**emp_dict, tenant_id=tenant_id, employee_name=computed_name)
    
    # 4. Add Children
    for edu in edu_data:
        employee.education.append(models.EmployeeEducation(**edu.model_dump(), tenant_id=tenant_id))
    for ext in ext_work:
        employee.external_work_history.append(models.EmployeeExternalWorkHistory(**ext.model_dump(), tenant_id=tenant_id))
    for internal in int_work:
        employee.internal_work_history.append(models.EmployeeInternalWorkHistory(**internal.model_dump(), tenant_id=tenant_id))

    db.add(employee)
    await db.commit()
    
    # Eager load relationships for the response
    stmt = (
        select(models.Employee)
        .options(
            selectinload(models.Employee.education),
            selectinload(models.Employee.external_work_history),
            selectinload(models.Employee.internal_work_history)
        )
        .where(models.Employee.id == employee.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()

@employee_router.get("/", response_model=List[schemas.EmployeeResponse])
async def list_employees(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = (
        select(models.Employee)
        .options(
            selectinload(models.Employee.education),
            selectinload(models.Employee.external_work_history),
            selectinload(models.Employee.internal_work_history)
        )
        .where(models.Employee.tenant_id == tenant_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@employee_router.get("/{id}", response_model=schemas.EmployeeResponse)
async def get_employee(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = (
        select(models.Employee)
        .options(
            selectinload(models.Employee.education),
            selectinload(models.Employee.external_work_history),
            selectinload(models.Employee.internal_work_history)
        )
        .where(models.Employee.id == id, models.Employee.tenant_id == tenant_id)
    )
    result = await db.execute(stmt)
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


# --- Leave Management ---

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
