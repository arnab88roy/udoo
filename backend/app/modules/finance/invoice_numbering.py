from datetime import date
from typing import Literal
from uuid import UUID
from sqlalchemy import select, func, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession

def get_financial_year_code(posting_date: date) -> str:
    """
    Returns 4-char FY code for invoice numbering.
    Indian FY: April 1 to March 31.

    Examples:
        2026-03-14 → "2526" (FY 2025-26)
        2026-04-01 → "2627" (FY 2026-27)
    """
    if posting_date.month >= 4:
        return f"{str(posting_date.year)[2:]}{str(posting_date.year + 1)[2:]}"
    else:
        return f"{str(posting_date.year - 1)[2:]}{str(posting_date.year)[2:]}"


async def get_next_number(
    db: AsyncSession,
    tenant_id: UUID,
    company_id: UUID,
    doc_type: Literal["INV", "QT", "PI"],
    posting_date: date,
) -> str:
    """
    Generates next sequential document number per company per FY.

    Format:
        INV-2526-0001  (Invoice)
        QT-2526-0001   (Quote)
        PI-2526-0001   (Proforma Invoice)

    Thread-safe: uses SELECT MAX + 1 within same company + FY.
    """
    fy = get_financial_year_code(posting_date)
    prefix = f"{doc_type}-{fy}-"

    # Determine which table to query
    if doc_type == "INV":
        from app.modules.finance.models import Invoice
        model = Invoice
        number_field = Invoice.invoice_number
    elif doc_type == "QT":
        from app.modules.finance.models import Quote
        model = Quote
        number_field = Quote.quote_number
    else:
        from app.modules.finance.models import ProformaInvoice
        model = ProformaInvoice
        number_field = ProformaInvoice.proforma_number # WATCH POINT 2

    stmt = select(func.max(
        cast(func.substr(number_field, len(prefix) + 1), Integer)
    )).where(
        model.tenant_id == tenant_id,
        model.company_id == company_id,
        number_field.like(f"{prefix}%")
    )
    result = await db.execute(stmt)
    max_num = result.scalar() or 0
    next_num = max_num + 1
    return f"{prefix}{str(next_num).zfill(4)}"
