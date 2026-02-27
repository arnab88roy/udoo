from typing import List, Type, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.dependencies import get_tenant_id
from app.modules.core_masters import models, schemas

router = APIRouter(prefix="/core-masters", tags=["Core Masters"])

# Generic CRUD helpers to avoid duplicating code for 7 identical simple masters
async def get_all_records(db: AsyncSession, model: Type[Any], tenant_id: str, skip: int = 0, limit: int = 100):
    # Using tenant_id string here loosely if string was defined, but schema uses UUID.
    # Postgres RLS will isolate at DB level if setup correctly via session parameters, 
    # but filtering at app-level provides double safety.
    query = select(model).filter(model.tenant_id == tenant_id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_record_by_id(db: AsyncSession, model: Type[Any], record_id: UUID, tenant_id: str):
    query = select(model).filter(model.id == record_id, model.tenant_id == tenant_id)
    result = await db.execute(query)
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return record

async def create_record(db: AsyncSession, model: Type[Any], schema: Any, tenant_id: str):
    db_record = model(**schema.model_dump(), tenant_id=tenant_id)
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record

async def update_record(db: AsyncSession, model: Type[Any], record_id: UUID, schema: Any, tenant_id: str):
    db_record = await get_record_by_id(db, model, record_id, tenant_id)
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    await db.commit()
    await db.refresh(db_record)
    return db_record

async def delete_record(db: AsyncSession, model: Type[Any], record_id: UUID, tenant_id: str):
    db_record = await get_record_by_id(db, model, record_id, tenant_id)
    await db.delete(db_record)
    await db.commit()
    return {"ok": True}

# ================================
# COMPANY
# ================================
@router.post("/companies/", response_model=schemas.CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(company: schemas.CompanyCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.Company, company, tenant_id)

@router.get("/companies/", response_model=List[schemas.CompanyResponse])
async def read_companies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.Company, tenant_id, skip, limit)

@router.get("/companies/{company_id}", response_model=schemas.CompanyResponse)
async def read_company(company_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.Company, company_id, tenant_id)

@router.put("/companies/{company_id}", response_model=schemas.CompanyResponse)
async def update_company(company_id: UUID, company: schemas.CompanyUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.Company, company_id, company, tenant_id)

@router.delete("/companies/{company_id}")
async def delete_company(company_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.Company, company_id, tenant_id)

# ================================
# BRANCH
# ================================
@router.post("/branches/", response_model=schemas.BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(branch: schemas.BranchCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.Branch, branch, tenant_id)

@router.get("/branches/", response_model=List[schemas.BranchResponse])
async def read_branches(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.Branch, tenant_id, skip, limit)

@router.get("/branches/{branch_id}", response_model=schemas.BranchResponse)
async def read_branch(branch_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.Branch, branch_id, tenant_id)

@router.put("/branches/{branch_id}", response_model=schemas.BranchResponse)
async def update_branch(branch_id: UUID, branch: schemas.BranchUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.Branch, branch_id, branch, tenant_id)

@router.delete("/branches/{branch_id}")
async def delete_branch(branch_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.Branch, branch_id, tenant_id)

# ================================
# GENDER
# ================================
@router.post("/genders/", response_model=schemas.GenderResponse, status_code=status.HTTP_201_CREATED)
async def create_gender(gender: schemas.GenderCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.Gender, gender, tenant_id)

@router.get("/genders/", response_model=List[schemas.GenderResponse])
async def read_genders(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.Gender, tenant_id, skip, limit)

@router.get("/genders/{gender_id}", response_model=schemas.GenderResponse)
async def read_gender(gender_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.Gender, gender_id, tenant_id)

@router.put("/genders/{gender_id}", response_model=schemas.GenderResponse)
async def update_gender(gender_id: UUID, gender: schemas.GenderUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.Gender, gender_id, gender, tenant_id)

@router.delete("/genders/{gender_id}")
async def delete_gender(gender_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.Gender, gender_id, tenant_id)

# ================================
# SALUTATION
# ================================
@router.post("/salutations/", response_model=schemas.SalutationResponse, status_code=status.HTTP_201_CREATED)
async def create_salutation(salutation: schemas.SalutationCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.Salutation, salutation, tenant_id)

@router.get("/salutations/", response_model=List[schemas.SalutationResponse])
async def read_salutations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.Salutation, tenant_id, skip, limit)

@router.get("/salutations/{salutation_id}", response_model=schemas.SalutationResponse)
async def read_salutation(salutation_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.Salutation, salutation_id, tenant_id)

@router.put("/salutations/{salutation_id}", response_model=schemas.SalutationResponse)
async def update_salutation(salutation_id: UUID, salutation: schemas.SalutationUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.Salutation, salutation_id, salutation, tenant_id)

@router.delete("/salutations/{salutation_id}")
async def delete_salutation(salutation_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.Salutation, salutation_id, tenant_id)

# ================================
# EMPLOYMENT TYPE
# ================================
@router.post("/employment-types/", response_model=schemas.EmploymentTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_employment_type(employment_type: schemas.EmploymentTypeCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.EmploymentType, employment_type, tenant_id)

@router.get("/employment-types/", response_model=List[schemas.EmploymentTypeResponse])
async def read_employment_types(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.EmploymentType, tenant_id, skip, limit)

@router.get("/employment-types/{employment_type_id}", response_model=schemas.EmploymentTypeResponse)
async def read_employment_type(employment_type_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.EmploymentType, employment_type_id, tenant_id)

@router.put("/employment-types/{employment_type_id}", response_model=schemas.EmploymentTypeResponse)
async def update_employment_type(employment_type_id: UUID, employment_type: schemas.EmploymentTypeUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.EmploymentType, employment_type_id, employment_type, tenant_id)

@router.delete("/employment-types/{employment_type_id}")
async def delete_employment_type(employment_type_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.EmploymentType, employment_type_id, tenant_id)

# ================================
# DESIGNATION
# ================================
@router.post("/designations/", response_model=schemas.DesignationResponse, status_code=status.HTTP_201_CREATED)
async def create_designation(designation: schemas.DesignationCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.Designation, designation, tenant_id)

@router.get("/designations/", response_model=List[schemas.DesignationResponse])
async def read_designations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.Designation, tenant_id, skip, limit)

@router.get("/designations/{designation_id}", response_model=schemas.DesignationResponse)
async def read_designation(designation_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.Designation, designation_id, tenant_id)

@router.put("/designations/{designation_id}", response_model=schemas.DesignationResponse)
async def update_designation(designation_id: UUID, designation: schemas.DesignationUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.Designation, designation_id, designation, tenant_id)

@router.delete("/designations/{designation_id}")
async def delete_designation(designation_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.Designation, designation_id, tenant_id)

# ================================
# SKILL
# ================================
@router.post("/skills/", response_model=schemas.SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(skill: schemas.SkillCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.Skill, skill, tenant_id)

@router.get("/skills/", response_model=List[schemas.SkillResponse])
async def read_skills(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.Skill, tenant_id, skip, limit)

@router.get("/skills/{skill_id}", response_model=schemas.SkillResponse)
async def read_skill(skill_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.Skill, skill_id, tenant_id)

@router.put("/skills/{skill_id}", response_model=schemas.SkillResponse)
async def update_skill(skill_id: UUID, skill: schemas.SkillUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.Skill, skill_id, skill, tenant_id)

@router.delete("/skills/{skill_id}")
async def delete_skill(skill_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.Skill, skill_id, tenant_id)

# ================================
# CURRENCY
# ================================
@router.post("/currencies/", response_model=schemas.CurrencyResponse, status_code=status.HTTP_201_CREATED)
async def create_currency(currency: schemas.CurrencyCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.Currency, currency, tenant_id)

@router.get("/currencies/", response_model=List[schemas.CurrencyResponse])
async def read_currencies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.Currency, tenant_id, skip, limit)

@router.get("/currencies/{currency_id}", response_model=schemas.CurrencyResponse)
async def read_currency(currency_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.Currency, currency_id, tenant_id)

@router.put("/currencies/{currency_id}", response_model=schemas.CurrencyResponse)
async def update_currency(currency_id: UUID, currency: schemas.CurrencyUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.Currency, currency_id, currency, tenant_id)

@router.delete("/currencies/{currency_id}")
async def delete_currency(currency_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.Currency, currency_id, tenant_id)

# ================================
# USER
# ================================
@router.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await create_record(db, models.User, user, tenant_id)

@router.get("/users/", response_model=List[schemas.UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_all_records(db, models.User, tenant_id, skip, limit)

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await get_record_by_id(db, models.User, user_id, tenant_id)

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: UUID, user: schemas.UserUpdate, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await update_record(db, models.User, user_id, user, tenant_id)

@router.delete("/users/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await delete_record(db, models.User, user_id, tenant_id)
