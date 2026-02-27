from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.dependencies import get_tenant_id
from app.modules.org_masters import models, schemas

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=schemas.DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    entity: schemas.DepartmentCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    db_obj = models.Department(**entity.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    try:
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.DepartmentResponse])
async def list_departments(
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    stmt = select(models.Department).where(models.Department.tenant_id == tenant_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{id}", response_model=schemas.DepartmentResponse)
async def get_department(
    id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(models.Department).where(models.Department.id == id, models.Department.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(status_code=404, detail="Department not found")
    return obj

# --- Employee Grade Endpoints ---
@router.post("/employee-grades", response_model=schemas.EmployeeGradeResponse)
async def create_employee_grade(data: schemas.EmployeeGradeCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    grade = models.EmployeeGrade(**data.model_dump(), tenant_id=tenant_id)
    db.add(grade)
    await db.commit()
    await db.refresh(grade)
    return grade

@router.get("/employee-grades", response_model=List[schemas.EmployeeGradeResponse])
async def list_employee_grades(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    result = await db.execute(select(models.EmployeeGrade).where(models.EmployeeGrade.tenant_id == tenant_id))
    return result.scalars().all()
