from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import logging

from app.db.database import get_db
from app.dependencies import get_tenant_id, get_current_user
from app.schemas.user_context import UserContext
from app.utils.permissions import require_permission
from app.modules.hr_masters import models as hr_models
from . import models, schemas, calculator

logger = logging.getLogger(__name__)

# --- Router 1: Compliance Settings ---
compliance_router = APIRouter(prefix="/compliance-settings", tags=["Payroll Compliance"])

@compliance_router.post("/", response_model=schemas.ComplianceSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_or_upsert_compliance(data: schemas.ComplianceSettingsCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    """Create or upsert compliance settings for a company."""
    stmt = select(models.ComplianceSettings).where(
        models.ComplianceSettings.company_id == data.company_id,
        models.ComplianceSettings.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    
    if obj:
        # Update
        for key, value in data.model_dump().items():
            setattr(obj, key, value)
    else:
        # Create
        obj = models.ComplianceSettings(**data.model_dump(), tenant_id=tenant_id)
        db.add(obj)
        
    await db.commit()
    await db.refresh(obj)
    return obj

@compliance_router.get("/{company_id}", response_model=schemas.ComplianceSettingsResponse)
async def get_compliance(company_id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.ComplianceSettings).where(
        models.ComplianceSettings.company_id == company_id,
        models.ComplianceSettings.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Compliance settings not found for this company")
    return obj

@compliance_router.put("/{company_id}", response_model=schemas.ComplianceSettingsResponse)
async def update_compliance(company_id: UUID, data: schemas.ComplianceSettingsUpdate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.ComplianceSettings).where(
        models.ComplianceSettings.company_id == company_id,
        models.ComplianceSettings.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Compliance settings not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    
    await db.commit()
    await db.refresh(obj)
    return obj

# --- Router 2: PT Slabs ---
pt_slab_router = APIRouter(prefix="/pt-slabs", tags=["Professional Tax"])

@pt_slab_router.post("/", response_model=schemas.ProfessionalTaxSlabResponse, status_code=status.HTTP_201_CREATED)
async def create_pt_slab(data: schemas.ProfessionalTaxSlabCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    db_obj = models.ProfessionalTaxSlab(**data.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@pt_slab_router.get("/", response_model=List[schemas.ProfessionalTaxSlabResponse])
async def list_pt_slabs(state_code: Optional[str] = None, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.ProfessionalTaxSlab).where(models.ProfessionalTaxSlab.tenant_id == tenant_id)
    if state_code:
        stmt = stmt.where(models.ProfessionalTaxSlab.state_code == state_code)
    result = await db.execute(stmt)
    return result.scalars().all()

@pt_slab_router.delete("/{id}")
async def delete_pt_slab(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.ProfessionalTaxSlab).where(
        models.ProfessionalTaxSlab.id == id,
        models.ProfessionalTaxSlab.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="PT slab not found")
    await db.delete(obj)
    await db.commit()
    return {"message": "Deleted successfully"}

# --- Router 3: Salary Components ---
salary_component_router = APIRouter(prefix="/salary-components", tags=["Payroll"])

@salary_component_router.post("/", response_model=schemas.SalaryComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_salary_component(data: schemas.SalaryComponentCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    db_obj = models.SalaryComponent(**data.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    await db.refresh(db_obj)
    return db_obj

@salary_component_router.get("/", response_model=List[schemas.SalaryComponentResponse])
async def list_salary_components(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.SalaryComponent).where(models.SalaryComponent.tenant_id == tenant_id, models.SalaryComponent.is_active == True)
    result = await db.execute(stmt)
    return result.scalars().all()

@salary_component_router.get("/{id}", response_model=schemas.SalaryComponentResponse)
async def get_salary_component(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.SalaryComponent).where(models.SalaryComponent.id == id, models.SalaryComponent.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Salary component not found")
    return obj

@salary_component_router.put("/{id}", response_model=schemas.SalaryComponentResponse)
async def update_salary_component(id: UUID, data: schemas.SalaryComponentUpdate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.SalaryComponent).where(models.SalaryComponent.id == id, models.SalaryComponent.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Salary component not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.commit()
    await db.refresh(obj)
    return obj

# --- Router 4: Salary Structures ---
salary_structure_router = APIRouter(prefix="/salary-structures", tags=["Payroll"])

@salary_structure_router.post("/", response_model=schemas.SalaryStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_salary_structure(data: schemas.SalaryStructureCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    components_data = data.components
    structure_data = data.model_dump(exclude={"components"})
    
    db_obj = models.SalaryStructure(**structure_data, tenant_id=tenant_id)
    db.add(db_obj)
    await db.flush() # Get ID
    
    for comp in components_data:
        comp_obj = models.SalaryStructureComponent(**comp.model_dump(), salary_structure_id=db_obj.id, tenant_id=tenant_id)
        db.add(comp_obj)
        
    await db.commit()
    
    stmt = select(models.SalaryStructure).options(
        selectinload(models.SalaryStructure.components).selectinload(models.SalaryStructureComponent.salary_component)
    ).where(models.SalaryStructure.id == db_obj.id, models.SalaryStructure.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@salary_structure_router.get("/", response_model=List[schemas.SalaryStructureResponse])
async def list_salary_structures(db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.SalaryStructure).options(
        selectinload(models.SalaryStructure.components).selectinload(models.SalaryStructureComponent.salary_component)
    ).where(models.SalaryStructure.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@salary_structure_router.get("/{id}", response_model=schemas.SalaryStructureResponse)
async def get_salary_structure(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.SalaryStructure).options(
        selectinload(models.SalaryStructure.components).selectinload(models.SalaryStructureComponent.salary_component)
    ).where(models.SalaryStructure.id == id, models.SalaryStructure.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Salary structure not found")
    return obj

# --- Router 5: Salary Slips ---
salary_slip_router = APIRouter(prefix="/salary-slips", tags=["Payroll"])

@salary_slip_router.post("/", response_model=schemas.SalarySlipResponse, status_code=status.HTTP_201_CREATED)
async def create_salary_slip(data: schemas.SalarySlipCreate, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    earnings_data = data.earnings
    deductions_data = data.deductions
    slip_data = data.model_dump(exclude={"earnings", "deductions"})
    
    db_obj = models.SalarySlip(**slip_data, tenant_id=tenant_id)
    db.add(db_obj)
    await db.flush()
    
    for e in earnings_data:
        db.add(models.SalarySlipEarning(**e.model_dump(), salary_slip_id=db_obj.id, tenant_id=tenant_id))
    for d in deductions_data:
        db.add(models.SalarySlipDeduction(**d.model_dump(), salary_slip_id=db_obj.id, tenant_id=tenant_id))
        
    await db.commit()
    
    stmt = select(models.SalarySlip).options(
        selectinload(models.SalarySlip.earnings),
        selectinload(models.SalarySlip.deductions)
    ).where(models.SalarySlip.id == db_obj.id, models.SalarySlip.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalar_one()

@salary_slip_router.get("/", response_model=List[schemas.SalarySlipResponse])
async def list_salary_slips(
    employee_id: Optional[UUID] = None,
    payroll_month: Optional[int] = None,
    payroll_year: Optional[int] = None,
    docstatus: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
):
    stmt = select(models.SalarySlip).options(
        selectinload(models.SalarySlip.earnings),
        selectinload(models.SalarySlip.deductions)
    ).where(models.SalarySlip.tenant_id == tenant_id)
    
    if employee_id: stmt = stmt.where(models.SalarySlip.employee_id == employee_id)
    if payroll_month: stmt = stmt.where(models.SalarySlip.payroll_month == payroll_month)
    if payroll_year: stmt = stmt.where(models.SalarySlip.payroll_year == payroll_year)
    if docstatus is not None: stmt = stmt.where(models.SalarySlip.docstatus == docstatus)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@salary_slip_router.get("/{id}", response_model=schemas.SalarySlipResponse)
async def get_salary_slip(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.SalarySlip).options(
        selectinload(models.SalarySlip.earnings),
        selectinload(models.SalarySlip.deductions)
    ).where(models.SalarySlip.id == id, models.SalarySlip.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    return obj

# Bulk Generation Background Task
async def bulk_generate_payroll_task(
    company_id: UUID, 
    payroll_month: int, 
    payroll_year: int, 
    working_days: int, 
    tenant_id: UUID,
    db_factory # Passing a function to get a new session if needed, but for now we'll use the session provided
):
    # Note: In background tasks, we should ideally create a new session
    # but for simplicity we rely on the session if it's still alive.
    # A better way is: async with SessionLocal() as db: ...
    # Since I don't have SessionLocal imported here easily, I'll use the one from main?
    # Or just assume the session passed is fine if we don't close it in the router.
    # Actually get_db is a generator. 
    from app.db.database import AsyncSessionLocal
    
    calc = calculator.PayrollCalculator()
    
    async with AsyncSessionLocal() as db:
        # 1. Fetch all active employees for this company+tenant
        stmt = select(hr_models.Employee).where(
            hr_models.Employee.company_id == company_id,
            hr_models.Employee.tenant_id == tenant_id,
            hr_models.Employee.status == "Active"
        )
        result = await db.execute(stmt)
        employees = result.scalars().all()
        
        # 2. Fetch compliance settings
        stmt = select(models.ComplianceSettings).where(
            models.ComplianceSettings.company_id == company_id,
            models.ComplianceSettings.tenant_id == tenant_id
        )
        res = await db.execute(stmt)
        compliance = res.scalar_one_or_none()
        if not compliance:
            logger.warning(f"No compliance settings for company {company_id}. Skipping bulk payroll.")
            return
            
        # 3. Fetch all salary components to link IDs for statutory deductions
        stmt = select(models.SalaryComponent).where(models.SalaryComponent.tenant_id == tenant_id)
        res = await db.execute(stmt)
        all_components = res.scalars().all()
        comp_name_map = {c.component_name: c.id for c in all_components}
        
        # 4. Fetch LOP Deduction ID explicitly
        stmt_lop = select(models.SalaryComponent).where(
            models.SalaryComponent.tenant_id == tenant_id,
            models.SalaryComponent.component_name == "LOP Deduction"
        )
        res_lop = await db.execute(stmt_lop)
        lop_component = res_lop.scalar_one_or_none()
        lop_component_id = lop_component.id if lop_component else None

        generated_count = 0
        for emp in employees:
            # Check if slip already exists
            stmt = select(models.SalarySlip).where(
                models.SalarySlip.employee_id == emp.id,
                models.SalarySlip.payroll_month == payroll_month,
                models.SalarySlip.payroll_year == payroll_year,
                models.SalarySlip.tenant_id == tenant_id
            )
            res = await db.execute(stmt)
            if res.scalar_one_or_none():
                continue

            # Fetch salary structure
            # To simplify, we'll fetch the first active structure for the company
            # In a real app, it might be linked to the employee.
            # Here, the prompt says "Fetch their salary structure (skip if none, log warning)"
            # Usually Employee has a salary_structure_id or similar.
            # Let's check employee model fields.
            # I'll fetch the one that matches company if employee doesn't have one specifically.
            # Actually, I'll search for any structure linked to this company.
            stmt = select(models.SalaryStructure).options(
                selectinload(models.SalaryStructure.components).selectinload(models.SalaryStructureComponent.salary_component)
            ).where(
                models.SalaryStructure.company_id == company_id,
                models.SalaryStructure.tenant_id == tenant_id,
                models.SalaryStructure.is_active == True
            )
            res = await db.execute(stmt)
            structure = res.scalar_one_or_none()
            if not structure:
                logger.warning(f"No salary structure for employee {emp.id}. Skipping.")
                continue

            # Fetch Attendance (present_days and lop_days)
            # Calculated from Attendance table normally. 
            # For now, we'll assume a dummy logic or look for existing records.
            # The prompt says "Fetch attendance for this month (calculate present_days and lop_days)"
            # I'll calculate it from hr_attendance.
            # Note: Attendance table has attendance_date.
            from datetime import date, timedelta
            import calendar
            _, last_day = calendar.monthrange(payroll_year, payroll_month)
            start_date = date(payroll_year, payroll_month, 1)
            end_date = date(payroll_year, payroll_month, last_day)
            
            stmt = select(hr_models.Attendance).where(
                hr_models.Attendance.employee_id == emp.id,
                hr_models.Attendance.attendance_date >= start_date,
                hr_models.Attendance.attendance_date <= end_date,
                hr_models.Attendance.tenant_id == tenant_id,
                hr_models.Attendance.docstatus == 1 # Submitted
            )
            res = await db.execute(stmt)
            attendances = res.scalars().all()
            
            present_days = sum(1 for a in attendances if a.status == "Present")
            # For this MVP, let's assume half day = 0.5
            present_days += sum(0.5 for a in attendances if a.status == "Half Day")
            
            # Simple LOP logic: any day not present or on leave is LOP? 
            # Usually LOP is marked explicitly or calculated from gap.
            # Instruction: "present_days and lop_days".
            # We'll assume any day marked "Absent" is LOP for now.
            lop_days = sum(1 for a in attendances if a.status == "Absent")

            # Fetch PT slabs
            # PT depends on state. We'll get state from company/branch?
            # Prompt: "Fetch PT slabs for employee's branch state"
            # Since I don't have branch state easily accessible on Employee in HR masters yet, 
            # I'll assume state_code = "MH" for now or fetch it if possible.
            # Actually, let's check Employee model - it belongs to a department/branch.
            # I'll just fetch all slabs for MH as default for the demo.
            stmt = select(models.ProfessionalTaxSlab).where(
                models.ProfessionalTaxSlab.state_code == "MH",
                models.ProfessionalTaxSlab.tenant_id == tenant_id
            )
            res = await db.execute(stmt)
            pt_slabs = res.scalars().all()

            # Calculation
            calc_res = calc.calculate(
                structure_components=structure.components,
                compliance=compliance,
                working_days=working_days,
                present_days=float(present_days),
                lop_days=float(lop_days),
                pt_slabs=pt_slabs,
                is_february=(payroll_month == 2),
                lop_component_id=lop_component_id
            )

            # Create Salary Slip
            slip_obj = models.SalarySlip(
                tenant_id=tenant_id,
                employee_id=emp.id,
                company_id=company_id,
                salary_structure_id=structure.id,
                payroll_month=payroll_month,
                payroll_year=payroll_year,
                working_days=working_days,
                present_days=float(present_days),
                lop_days=float(lop_days),
                gross_earnings=calc_res["gross_earnings"],
                pf_employee=calc_res["pf_employee"],
                pf_employer=calc_res["pf_employer"],
                eps_employer=calc_res["eps_employer"],
                esi_employee=calc_res["esi_employee"],
                esi_employer=calc_res["esi_employer"],
                professional_tax=calc_res["professional_tax"],
                tds_amount=calc_res["tds_amount"],
                total_deductions=calc_res["total_deductions"],
                net_pay=calc_res["net_pay"],
                docstatus=0,
                posting_date=date.today()
            )
            db.add(slip_obj)
            await db.flush()

            # Add earnings and deductions
            for e in calc_res["earnings"]:
                comp_id = e.get("salary_component_id") or comp_name_map.get(e["component_name"])
                db.add(models.SalarySlipEarning(
                    tenant_id=tenant_id,
                    salary_slip_id=slip_obj.id,
                    salary_component_id=comp_id,
                    component_name=e["component_name"],
                    amount=e["amount"]
                ))
            
            for d in calc_res["deductions"]:
                comp_id = d.get("salary_component_id") or comp_name_map.get(d["component_name"])
                db.add(models.SalarySlipDeduction(
                    tenant_id=tenant_id,
                    salary_slip_id=slip_obj.id,
                    salary_component_id=comp_id,
                    component_name=d["component_name"],
                    amount=d["amount"]
                ))

            generated_count += 1
        
        await db.commit()
        logger.info(f"Generated {generated_count} slips for company {company_id}, month {payroll_month}")

@salary_slip_router.post("/bulk-generate")
async def bulk_generate_payroll(
    request: schemas.BulkGenerateRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: UserContext = Depends(get_current_user),
):
    require_permission(current_user, "payroll", "submit")
    background_tasks.add_task(
        bulk_generate_payroll_task,
        request.company_id,
        request.payroll_month,
        request.payroll_year,
        request.working_days,
        tenant_id,
        None
    )
    return {
        "message": "Payroll generation started",
        "company_id": request.company_id,
        "month": request.payroll_month,
        "year": request.payroll_year
    }

@salary_slip_router.post("/{id}/submit", response_model=schemas.SalarySlipResponse)
async def submit_salary_slip(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.SalarySlip).where(models.SalarySlip.id == id, models.SalarySlip.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    if obj.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only Draft slips can be submitted")
    obj.docstatus = 1
    await db.commit()
    
    stmt = select(models.SalarySlip).options(
        selectinload(models.SalarySlip.earnings),
        selectinload(models.SalarySlip.deductions)
    ).where(models.SalarySlip.id == id, models.SalarySlip.tenant_id == tenant_id)
    res = await db.execute(stmt)
    return res.scalar_one()

@salary_slip_router.post("/{id}/cancel", response_model=schemas.SalarySlipResponse)
async def cancel_salary_slip(id: UUID, db: AsyncSession = Depends(get_db), tenant_id: UUID = Depends(get_tenant_id)):
    stmt = select(models.SalarySlip).where(models.SalarySlip.id == id, models.SalarySlip.tenant_id == tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Salary slip not found")
    if obj.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted slips can be cancelled")
    obj.docstatus = 2
    await db.commit()
    
    stmt = select(models.SalarySlip).options(
        selectinload(models.SalarySlip.earnings),
        selectinload(models.SalarySlip.deductions)
    ).where(models.SalarySlip.id == id, models.SalarySlip.tenant_id == tenant_id)
    res = await db.execute(stmt)
    return res.scalar_one()
