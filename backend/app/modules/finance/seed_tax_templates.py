import asyncio
from uuid import UUID
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.modules.finance.models import TaxTemplate, TaxTemplateLine
from app.modules.core_masters.models import Company

async def seed_tax_templates():
    async with AsyncSessionLocal() as db:
        # Get all tenants/companies current to seed for
        stmt = select(Company)
        result = await db.execute(stmt)
        companies = result.scalars().all()
        
        for company in companies:
            print(f"Seeding for Company: {company.company_name} (Tenant: {company.tenant_id})")
            
            # 1. GST 18% (Standard GST)
            stmt = select(TaxTemplate).where(
                TaxTemplate.tenant_id == company.tenant_id,
                TaxTemplate.template_name == "GST 18%"
            )
            existing = await db.execute(stmt)
            if not existing.scalar_one_or_none():
                template = TaxTemplate(
                    template_name="GST 18%",
                    country_code="IN",
                    description="Standard Indian GST (9% CGST + 9% SGST or 18% IGST)",
                    tenant_id=company.tenant_id
                )
                db.add(template)
                await db.flush()
                
                # Add Line
                line = TaxTemplateLine(
                    tax_name="IGST",
                    rate=18.0,
                    is_inclusive=False,
                    order_index=1,
                    tax_template_id=template.id,
                    tenant_id=company.tenant_id
                )
                db.add(line)
            
            # 2. Zero Rated (Exports)
            stmt = select(TaxTemplate).where(
                TaxTemplate.tenant_id == company.tenant_id,
                TaxTemplate.template_name == "Zero Rated"
            )
            existing = await db.execute(stmt)
            if not existing.scalar_one_or_none():
                template = TaxTemplate(
                    template_name="Zero Rated",
                    country_code=None,
                    description="Zero tax for Exports or Exempted goods",
                    tenant_id=company.tenant_id
                )
                db.add(template)
                await db.flush()
                
                line = TaxTemplateLine(
                    tax_name="Zero Tax",
                    rate=0.0,
                    is_inclusive=False,
                    order_index=1,
                    tax_template_id=template.id,
                    tenant_id=company.tenant_id
                )
                db.add(line)

        await db.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_tax_templates())
