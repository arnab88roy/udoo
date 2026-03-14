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
