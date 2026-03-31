from typing import List, Optional, Literal
from uuid import UUID
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.utils.permissions import require_permission
from app.schemas.user_context import UserContext
from app.dependencies import get_current_user

from app.modules.finance.models import (
    ExchangeRateConfig, TaxTemplate, TaxTemplateLine, Client, TDSConfig,
    Quote, QuoteLineItem, ProformaInvoice, ProformaLineItem, Invoice,
    InvoiceLineItem, Payment, RecurringInvoiceConfig
)
from app.modules.finance.schemas import (
    ExchangeRateConfigCreate, ExchangeRateConfigResponse,
    TaxTemplateCreate, TaxTemplateResponse, TaxTemplateUpdate,
    ClientCreate, ClientUpdate, ClientResponse,
    TDSConfigUpdate, TDSConfigResponse,
    QuoteCreate, QuoteUpdate, QuoteResponse,
    ProformaCreate, ProformaResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    PaymentCreate, PaymentResponse, PaymentBase,
    RecurringInvoiceConfigCreate, RecurringInvoiceConfigUpdate, RecurringInvoiceConfigResponse,
    ConvertToInvoiceRequest, FetchExchangeRateRequest, FetchExchangeRateResponse
)
from app.modules.finance.gst_calculator import GSTCalculator
from app.modules.finance.exchange_rate import fetch_exchange_rate
from app.modules.finance.invoice_numbering import get_next_number

# --- Routers ---
exchange_rate_router = APIRouter(tags=["Finance - Exchange Rates"])
tax_template_router = APIRouter(tags=["Finance - Tax Templates"])
client_router = APIRouter(tags=["Finance - Clients"])
quote_router = APIRouter(tags=["Finance - Quotes"])
proforma_router = APIRouter(tags=["Finance - Proforma Invoices"])
invoice_router = APIRouter(tags=["Finance - Invoices"])
payment_router = APIRouter(tags=["Finance - Payments"])
recurring_router = APIRouter(tags=["Finance - Recurring Invoices"])
salary_slip_html_router = APIRouter(tags=["Finance - Salary Slips"])
finance_reports_router = APIRouter(tags=["Finance - Reports"])


# ====== SHARED HELPER ======

async def _calculate_line_tax(
    db: AsyncSession,
    line_taxable: Decimal,
    tax_template_id,
    client_id: UUID,
    company_id: UUID,
    tenant_id: UUID,
) -> Decimal:
    """Calculate tax for a line item using GSTCalculator. Returns total_tax."""
    if not tax_template_id:
        return Decimal("0")

    stmt = select(TaxTemplateLine).where(
        TaxTemplateLine.tax_template_id == tax_template_id
    )
    lines_res = await db.execute(stmt)
    template_lines = [
        {"rate": l.rate, "tax_name": l.tax_name}
        for l in lines_res.scalars()
    ]

    from app.modules.core_masters.models import Client as ClientModel, Company
    stmt = select(ClientModel).where(ClientModel.id == client_id, ClientModel.tenant_id == tenant_id)
    cl_res = await db.execute(stmt)
    client_obj = cl_res.scalar_one()

    stmt = select(Company).where(Company.id == company_id, Company.tenant_id == tenant_id)
    co_res = await db.execute(stmt)
    company_obj = co_res.scalar_one()

    gst_type = GSTCalculator.determine_gst_type(
        company_obj.state_code,
        client_obj.state_code,
        client_obj.country_code
    )
    tax_breakdown = GSTCalculator.calculate_line_tax(
        line_taxable, template_lines, gst_type
    )
    return tax_breakdown["total_tax"]


# ====== ROUTER 1: Exchange Rate ======

@exchange_rate_router.post("/finance/exchange-rates/config", response_model=ExchangeRateConfigResponse, status_code=201)
async def upsert_exchange_rate_config(
    data: ExchangeRateConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "edit")
    stmt = select(ExchangeRateConfig).where(
        ExchangeRateConfig.tenant_id == current_user.tenant_id,
        ExchangeRateConfig.company_id == data.company_id
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if config:
        config.auto_fetch = data.auto_fetch
        config.api_provider = data.api_provider
    else:
        config = ExchangeRateConfig(**data.model_dump(), tenant_id=current_user.tenant_id)
        db.add(config)
    await db.commit()
    await db.refresh(config)
    return config

@exchange_rate_router.post("/finance/exchange-rates/fetch", response_model=FetchExchangeRateResponse)
async def fetch_live_rate(
    data: FetchExchangeRateRequest,
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    result = await fetch_exchange_rate(data.from_currency, data.to_currency)
    return result


# ====== ROUTER 2: Tax Templates ======

@tax_template_router.post("/finance/tax-templates/", response_model=TaxTemplateResponse, status_code=201)
async def create_tax_template(
    data: TaxTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")
    template = TaxTemplate(
        template_name=data.template_name,
        country_code=data.country_code,
        description=data.description,
        is_active=data.is_active,
        tenant_id=current_user.tenant_id
    )
    db.add(template)
    await db.flush()
    for line_data in data.lines:
        line = TaxTemplateLine(
            **line_data.model_dump(),
            tax_template_id=template.id,
            tenant_id=current_user.tenant_id
        )
        db.add(line)
    await db.commit()
    stmt = select(TaxTemplate).options(selectinload(TaxTemplate.lines)).where(TaxTemplate.id == template.id)
    result = await db.execute(stmt)
    return result.scalar_one()

@tax_template_router.get("/finance/tax-templates/", response_model=List[TaxTemplateResponse])
async def list_tax_templates(
    country_code: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(TaxTemplate).options(selectinload(TaxTemplate.lines)).where(
        TaxTemplate.tenant_id == current_user.tenant_id,
        TaxTemplate.is_active == True
    )
    if country_code:
        stmt = stmt.where(or_(TaxTemplate.country_code == country_code, TaxTemplate.country_code == None))
    result = await db.execute(stmt)
    return result.scalars().all()

@tax_template_router.get("/finance/tax-templates/{id}", response_model=TaxTemplateResponse)
async def get_tax_template(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(TaxTemplate).options(selectinload(TaxTemplate.lines)).where(
        TaxTemplate.id == id, TaxTemplate.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Tax template not found.")
    return obj


# ====== ROUTER 3: Clients ======

@client_router.post("/finance/clients/", response_model=ClientResponse, status_code=201)
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")
    client_dict = data.model_dump(exclude={"tds_config"})
    client = Client(**client_dict, tenant_id=current_user.tenant_id)
    db.add(client)
    await db.flush()
    tds_data = data.tds_config.model_dump() if data.tds_config else {"is_applicable": False}
    tds_config = TDSConfig(**tds_data, client_id=client.id, tenant_id=current_user.tenant_id)
    db.add(tds_config)
    await db.commit()
    stmt = select(Client).options(selectinload(Client.tds_config)).where(Client.id == client.id)
    result = await db.execute(stmt)
    return result.scalar_one()

@client_router.get("/finance/clients/", response_model=List[ClientResponse])
async def list_clients(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(Client).options(selectinload(Client.tds_config)).where(
        Client.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@client_router.get("/finance/clients/{id}", response_model=ClientResponse)
async def get_client(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(Client).options(selectinload(Client.tds_config)).where(
        Client.id == id, Client.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Client not found.")
    return obj


# ====== ROUTER 4: Quotes ======

@quote_router.post("/finance/quotes/", response_model=QuoteResponse, status_code=201)
async def create_quote(
    data: QuoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")
    quote_dict = data.model_dump(exclude={"line_items"})
    quote = Quote(**quote_dict, tenant_id=current_user.tenant_id)

    # Auto-fetch exchange rate if currencies differ
    if not quote.exchange_rate_locked:
        from app.modules.core_masters.models import Company, Currency
        stmt = select(Company).where(Company.id == quote.company_id)
        comp_res = await db.execute(stmt)
        company = comp_res.scalar_one()
        if company.base_currency_id and quote.currency_id and company.base_currency_id != quote.currency_id:
            stmt = select(Currency).where(Currency.id.in_([company.base_currency_id, quote.currency_id]))
            curr_res = await db.execute(stmt)
            currencies = {c.id: c.currency_code for c in curr_res.scalars()}
            rate_res = await fetch_exchange_rate(currencies[quote.currency_id], currencies[company.base_currency_id])
            if rate_res["success"]:
                quote.exchange_rate = Decimal(str(rate_res["rate"]))

    db.add(quote)
    await db.flush()

    subtotal = Decimal("0")
    total_tax = Decimal("0")
    for line_data in data.line_items:
        line = QuoteLineItem(**line_data.model_dump(), quote_id=quote.id, tenant_id=current_user.tenant_id)
        line.taxable_amount = (line.quantity * line.rate * (1 - line.discount_percent / 100)).quantize(Decimal("0.01"))
        effective_template = line.tax_template_id or quote.tax_template_id
        line.tax_amount = await _calculate_line_tax(db, line.taxable_amount, effective_template, quote.client_id, quote.company_id, current_user.tenant_id)
        line.line_total = line.taxable_amount + line.tax_amount
        db.add(line)
        subtotal += line.taxable_amount
        total_tax += line.tax_amount

    quote.subtotal = subtotal
    quote.total_tax = total_tax
    quote.total_amount = subtotal + total_tax
    quote.base_total_amount = quote.total_amount * quote.exchange_rate
    await db.commit()

    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.id == quote.id)
    result = await db.execute(stmt)
    return result.scalar_one()

@quote_router.get("/finance/quotes/", response_model=List[QuoteResponse])
async def list_quotes(
    client_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.tenant_id == current_user.tenant_id)
    if client_id:
        stmt = stmt.where(Quote.client_id == client_id)
    if status:
        stmt = stmt.where(Quote.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()

@quote_router.get("/finance/quotes/{id}", response_model=QuoteResponse)
async def get_quote(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "view")
    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.id == id, Quote.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Quote not found.")
    return obj

@quote_router.post("/finance/quotes/{id}/submit", response_model=QuoteResponse)
async def submit_quote(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "submit")
    stmt = select(Quote).where(Quote.id == id, Quote.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    quote = res.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")
    if quote.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only Draft quotes can be submitted.")
    quote.docstatus = 1
    quote.status = "Sent"
    quote.quote_number = await get_next_number(db, current_user.tenant_id, quote.company_id, "QT", quote.posting_date)
    quote.exchange_rate_locked = True
    await db.commit()
    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.id == quote.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@quote_router.post("/finance/quotes/{id}/accept", response_model=QuoteResponse)
async def accept_quote(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "approve")
    stmt = select(Quote).where(Quote.id == id, Quote.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    quote = res.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")
    if quote.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted quotes can be accepted.")
    quote.status = "Accepted"
    await db.commit()
    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.id == quote.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@quote_router.post("/finance/quotes/{id}/reject", response_model=QuoteResponse)
async def reject_quote(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "approve")
    stmt = select(Quote).where(Quote.id == id, Quote.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    quote = res.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")
    if quote.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted quotes can be rejected.")
    quote.status = "Rejected"
    await db.commit()
    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.id == quote.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@quote_router.post("/finance/quotes/{id}/cancel", response_model=QuoteResponse)
async def cancel_quote(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "delete")
    stmt = select(Quote).where(Quote.id == id, Quote.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    quote = res.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")
    if quote.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted quotes can be cancelled.")
    quote.docstatus = 2
    await db.commit()
    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.id == quote.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@quote_router.post("/finance/quotes/{id}/convert-to-invoice", response_model=InvoiceResponse)
async def convert_quote_to_invoice(
    id: UUID,
    data: ConvertToInvoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")
    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.id == id, Quote.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    quote = res.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")
    if quote.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted quotes can be converted.")

    # Create Invoice from Quote
    invoice = Invoice(
        tenant_id=current_user.tenant_id,
        company_id=quote.company_id,
        client_id=quote.client_id,
        currency_id=quote.currency_id,
        exchange_rate=quote.exchange_rate,
        exchange_rate_locked=False,
        tax_template_id=quote.tax_template_id,
        subtotal=quote.subtotal,
        total_tax=quote.total_tax,
        total_amount=quote.total_amount,
        base_total_amount=quote.base_total_amount,
        posting_date=data.posting_date,
        notes=quote.notes,
        terms=quote.terms,
        quote_id=quote.id,
        outstanding_amount=quote.total_amount,
    )
    if data.due_date:
        invoice.due_date = data.due_date
    else:
        stmt = select(Client).where(Client.id == quote.client_id)
        cl_res = await db.execute(stmt)
        client = cl_res.scalar_one()
        invoice.due_date = data.posting_date + timedelta(days=client.payment_terms_days)

    db.add(invoice)
    await db.flush()

    for q_line in quote.line_items:
        inv_line = InvoiceLineItem(
            tenant_id=current_user.tenant_id,
            invoice_id=invoice.id,
            description=q_line.description,
            hsn_sac_code=q_line.hsn_sac_code,
            quantity=q_line.quantity,
            rate=q_line.rate,
            discount_percent=q_line.discount_percent,
            taxable_amount=q_line.taxable_amount,
            tax_template_id=q_line.tax_template_id,
            tax_amount=q_line.tax_amount,
            line_total=q_line.line_total,
            order_index=q_line.order_index,
        )
        db.add(inv_line)

    quote.status = "Accepted"
    await db.commit()

    stmt = select(Invoice).options(selectinload(Invoice.line_items), selectinload(Invoice.payments)).where(Invoice.id == invoice.id)
    res = await db.execute(stmt)
    return res.scalar_one()


# ====== ROUTER 5: Proforma Invoices ======

@proforma_router.post("/finance/proforma-invoices/", response_model=ProformaResponse, status_code=201)
async def create_proforma(
    data: ProformaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")
    proforma_dict = data.model_dump(exclude={"line_items"})
    proforma = ProformaInvoice(**proforma_dict, tenant_id=current_user.tenant_id)
    db.add(proforma)
    await db.flush()

    subtotal = Decimal("0")
    total_tax = Decimal("0")
    for line_data in data.line_items:
        line = ProformaLineItem(**line_data.model_dump(), proforma_id=proforma.id, tenant_id=current_user.tenant_id)
        line.taxable_amount = (line.quantity * line.rate * (1 - line.discount_percent / 100)).quantize(Decimal("0.01"))
        effective_template = line.tax_template_id or proforma.tax_template_id
        line.tax_amount = await _calculate_line_tax(db, line.taxable_amount, effective_template, proforma.client_id, proforma.company_id, current_user.tenant_id)
        line.line_total = line.taxable_amount + line.tax_amount
        db.add(line)
        subtotal += line.taxable_amount
        total_tax += line.tax_amount

    proforma.subtotal = subtotal
    proforma.total_tax = total_tax
    proforma.total_amount = subtotal + total_tax
    proforma.base_total_amount = proforma.total_amount * proforma.exchange_rate
    await db.commit()

    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.id == proforma.id)
    result = await db.execute(stmt)
    return result.scalar_one()

@proforma_router.get("/finance/proforma-invoices/", response_model=List[ProformaResponse])
async def list_proformas(db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "view")
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@proforma_router.get("/finance/proforma-invoices/{id}", response_model=ProformaResponse)
async def get_proforma(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "view")
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.id == id, ProformaInvoice.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Proforma invoice not found.")
    return obj

@proforma_router.post("/finance/proforma-invoices/{id}/submit", response_model=ProformaResponse)
async def submit_proforma(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "submit")
    stmt = select(ProformaInvoice).where(ProformaInvoice.id == id, ProformaInvoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    proforma = res.scalar_one_or_none()
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma not found.")
    if proforma.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only Draft proformas can be submitted.")
    proforma.docstatus = 1
    proforma.status = "Sent"
    proforma.proforma_number = await get_next_number(db, current_user.tenant_id, proforma.company_id, "PI", proforma.posting_date)
    proforma.exchange_rate_locked = True
    await db.commit()
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.id == proforma.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@proforma_router.post("/finance/proforma-invoices/{id}/cancel", response_model=ProformaResponse)
async def cancel_proforma(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "delete")
    stmt = select(ProformaInvoice).where(ProformaInvoice.id == id, ProformaInvoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    proforma = res.scalar_one_or_none()
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma not found.")
    if proforma.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted proformas can be cancelled.")
    proforma.docstatus = 2
    await db.commit()
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.id == proforma.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@proforma_router.post("/finance/proforma-invoices/{id}/convert-to-invoice", response_model=InvoiceResponse)
async def convert_proforma_to_invoice(
    id: UUID,
    data: ConvertToInvoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.id == id, ProformaInvoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    proforma = res.scalar_one_or_none()
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma not found.")
    if proforma.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted proformas can be converted.")

    invoice = Invoice(
        tenant_id=current_user.tenant_id,
        company_id=proforma.company_id,
        client_id=proforma.client_id,
        currency_id=proforma.currency_id,
        exchange_rate=proforma.exchange_rate,
        exchange_rate_locked=False,
        tax_template_id=proforma.tax_template_id,
        subtotal=proforma.subtotal,
        total_tax=proforma.total_tax,
        total_amount=proforma.total_amount,
        base_total_amount=proforma.base_total_amount,
        posting_date=data.posting_date,
        notes=proforma.notes,
        terms=proforma.terms,
        proforma_id=proforma.id,
        outstanding_amount=proforma.total_amount,
    )
    if data.due_date:
        invoice.due_date = data.due_date
    else:
        stmt = select(Client).where(Client.id == proforma.client_id)
        cl_res = await db.execute(stmt)
        client = cl_res.scalar_one()
        invoice.due_date = data.posting_date + timedelta(days=client.payment_terms_days)

    db.add(invoice)
    await db.flush()

    for p_line in proforma.line_items:
        inv_line = InvoiceLineItem(
            tenant_id=current_user.tenant_id,
            invoice_id=invoice.id,
            description=p_line.description,
            hsn_sac_code=p_line.hsn_sac_code,
            quantity=p_line.quantity,
            rate=p_line.rate,
            discount_percent=p_line.discount_percent,
            taxable_amount=p_line.taxable_amount,
            tax_template_id=p_line.tax_template_id,
            tax_amount=p_line.tax_amount,
            line_total=p_line.line_total,
            order_index=p_line.order_index,
        )
        db.add(inv_line)

    await db.commit()
    stmt = select(Invoice).options(selectinload(Invoice.line_items), selectinload(Invoice.payments)).where(Invoice.id == invoice.id)
    res = await db.execute(stmt)
    return res.scalar_one()


# ====== ROUTER 6: Invoices ======

@invoice_router.post("/finance/invoices/", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")
    inv_dict = data.model_dump(exclude={"line_items"})
    invoice = Invoice(**inv_dict, tenant_id=current_user.tenant_id)

    if not invoice.due_date:
        stmt = select(Client).where(Client.id == invoice.client_id)
        cl_res = await db.execute(stmt)
        client = cl_res.scalar_one()
        invoice.due_date = invoice.posting_date + timedelta(days=client.payment_terms_days)

    db.add(invoice)
    await db.flush()

    subtotal = Decimal("0")
    total_tax = Decimal("0")
    for line_data in data.line_items:
        line = InvoiceLineItem(**line_data.model_dump(), invoice_id=invoice.id, tenant_id=current_user.tenant_id)
        line.taxable_amount = (line.quantity * line.rate * (1 - line.discount_percent / 100)).quantize(Decimal("0.01"))
        effective_template = line.tax_template_id or invoice.tax_template_id
        line.tax_amount = await _calculate_line_tax(db, line.taxable_amount, effective_template, invoice.client_id, invoice.company_id, current_user.tenant_id)
        line.line_total = line.taxable_amount + line.tax_amount
        db.add(line)
        subtotal += line.taxable_amount
        total_tax += line.tax_amount

    invoice.subtotal = subtotal
    invoice.total_tax = total_tax
    invoice.total_amount = subtotal + total_tax
    invoice.outstanding_amount = invoice.total_amount
    invoice.base_total_amount = invoice.total_amount * invoice.exchange_rate
    await db.commit()

    stmt = select(Invoice).options(selectinload(Invoice.line_items), selectinload(Invoice.payments)).where(Invoice.id == invoice.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@invoice_router.get("/finance/invoices/", response_model=List[InvoiceResponse])
async def list_invoices(
    client_id: Optional[UUID] = None,
    status: Optional[str] = None,
    overdue: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(Invoice).options(
        selectinload(Invoice.line_items), selectinload(Invoice.payments)
    ).where(Invoice.tenant_id == current_user.tenant_id)
    if client_id:
        stmt = stmt.where(Invoice.client_id == client_id)
    if status:
        stmt = stmt.where(Invoice.status == status)
    if overdue:
        stmt = stmt.where(Invoice.due_date < date.today(), Invoice.status != "Paid")
    result = await db.execute(stmt)
    return result.scalars().all()

@invoice_router.get("/finance/invoices/{id}", response_model=InvoiceResponse)
async def get_invoice(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "view")
    stmt = select(Invoice).options(
        selectinload(Invoice.line_items), selectinload(Invoice.payments)
    ).where(Invoice.id == id, Invoice.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return obj

@invoice_router.post("/finance/invoices/{id}/submit", response_model=InvoiceResponse)
async def submit_invoice(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "submit")
    stmt = select(Invoice).where(Invoice.id == id, Invoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    invoice = res.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    if invoice.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only Draft invoices can be submitted.")
    invoice.docstatus = 1
    invoice.status = "Sent"
    invoice.invoice_number = await get_next_number(db, current_user.tenant_id, invoice.company_id, "INV", invoice.posting_date)
    invoice.exchange_rate_locked = True
    await db.commit()
    stmt = select(Invoice).options(selectinload(Invoice.line_items), selectinload(Invoice.payments)).where(Invoice.id == invoice.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@invoice_router.post("/finance/invoices/{id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "delete")
    stmt = select(Invoice).where(Invoice.id == id, Invoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    invoice = res.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    if invoice.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only Submitted invoices can be cancelled.")
    if invoice.amount_paid > 0:
        raise HTTPException(status_code=400, detail="Cannot cancel an invoice with payments recorded.")
    invoice.docstatus = 2
    invoice.status = "Cancelled"
    await db.commit()
    stmt = select(Invoice).options(selectinload(Invoice.line_items), selectinload(Invoice.payments)).where(Invoice.id == invoice.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@invoice_router.post("/finance/invoices/{id}/payments", response_model=InvoiceResponse)
async def add_invoice_payment(
    id: UUID,
    data: PaymentBase,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "edit")
    stmt = select(Invoice).where(Invoice.id == id, Invoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    invoice = res.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    if invoice.docstatus != 1:
        raise HTTPException(status_code=400, detail="Payments can only be added to submitted invoices.")

    payment = Payment(**data.model_dump(), invoice_id=invoice.id, tenant_id=current_user.tenant_id)
    db.add(payment)

    # TDS deduction logic
    stmt = select(TDSConfig).where(TDSConfig.client_id == invoice.client_id)
    tds_res = await db.execute(stmt)
    tds_config = tds_res.scalar_one_or_none()
    if tds_config and tds_config.is_applicable:
        new_accumulated = tds_config.accumulated_payments_this_year + payment.amount_received
        if new_accumulated > tds_config.threshold_annual:
            payment.tds_deducted = (payment.amount_received * tds_config.rate / 100).quantize(Decimal("0.01"))
            payment.tds_section = tds_config.section
            tds_config.accumulated_payments_this_year = new_accumulated
            invoice.tds_amount += payment.tds_deducted

    # Atomic update — Rule 4
    invoice.amount_paid += payment.amount_received
    invoice.outstanding_amount = invoice.total_amount - invoice.amount_paid
    if invoice.outstanding_amount <= Decimal("0"):
        invoice.status = "Paid"
    else:
        invoice.status = "Partially Paid"

    await db.commit()
    stmt = select(Invoice).options(selectinload(Invoice.line_items), selectinload(Invoice.payments)).where(Invoice.id == invoice.id)
    res = await db.execute(stmt)
    return res.scalar_one()


# ====== ROUTER 7: Payments ======

@payment_router.get("/finance/payments/", response_model=List[PaymentResponse])
async def list_payments(
    invoice_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(Payment).where(Payment.tenant_id == current_user.tenant_id)
    if invoice_id:
        stmt = stmt.where(Payment.invoice_id == invoice_id)
    result = await db.execute(stmt)
    return result.scalars().all()


# ====== ROUTER 8: Recurring Invoices ======

@recurring_router.post("/finance/recurring-invoices/", response_model=RecurringInvoiceConfigResponse, status_code=201)
async def create_recurring(
    data: RecurringInvoiceConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")
    stmt = select(Invoice).where(Invoice.id == data.template_invoice_id, Invoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    template = res.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template invoice not found.")
    if template.docstatus != 1:
        raise HTTPException(status_code=400, detail="Template invoice must be submitted (docstatus=1).")
    config = RecurringInvoiceConfig(**data.model_dump(), tenant_id=current_user.tenant_id)
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config

@recurring_router.get("/finance/recurring-invoices/", response_model=List[RecurringInvoiceConfigResponse])
async def list_recurring(db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "view")
    stmt = select(RecurringInvoiceConfig).where(
        RecurringInvoiceConfig.tenant_id == current_user.tenant_id,
        RecurringInvoiceConfig.is_active == True
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@recurring_router.post("/finance/recurring-invoices/{id}/pause", response_model=RecurringInvoiceConfigResponse)
async def pause_recurring(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "edit")
    stmt = select(RecurringInvoiceConfig).where(RecurringInvoiceConfig.id == id, RecurringInvoiceConfig.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    config = res.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Recurring config not found.")
    config.is_active = False
    await db.commit()
    await db.refresh(config)
    return config

@recurring_router.post("/finance/recurring-invoices/{id}/resume", response_model=RecurringInvoiceConfigResponse)
async def resume_recurring(id: UUID, db: AsyncSession = Depends(get_db), current_user: UserContext = Depends(get_current_user)):
    require_permission(current_user, "finance", "edit")
    stmt = select(RecurringInvoiceConfig).where(RecurringInvoiceConfig.id == id, RecurringInvoiceConfig.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    config = res.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Recurring config not found.")
    config.is_active = True
    await db.commit()
    await db.refresh(config)
    return config


# ====== ROUTER 9: Salary Slip HTML ======

@salary_slip_html_router.get("/finance/salary-slips/{id}/html")
async def get_salary_slip_html(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")

    from app.modules.payroll.models import SalarySlip
    from app.modules.hr_masters.models import Employee
    from app.modules.core_masters.models import Company

    stmt = select(SalarySlip).options(
        selectinload(SalarySlip.earnings),
        selectinload(SalarySlip.deductions)
    ).where(SalarySlip.id == id, SalarySlip.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    slip = res.scalar_one_or_none()
    if not slip:
        raise HTTPException(status_code=404, detail="Salary slip not found.")

    emp_stmt = select(Employee).where(Employee.id == slip.employee_id)
    emp_res = await db.execute(emp_stmt)
    employee = emp_res.scalar_one_or_none()

    co_stmt = select(Company).where(Company.id == slip.company_id)
    co_res = await db.execute(co_stmt)
    company = co_res.scalar_one_or_none()

    emp_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown Employee"
    co_name = company.company_name if company else "Unknown Company"

    earnings = slip.earnings or []
    deductions = slip.deductions or []
    max_rows = max(len(earnings), len(deductions), 1)

    rows_html = ""
    for i in range(max_rows):
        e = earnings[i] if i < len(earnings) else None
        d = deductions[i] if i < len(deductions) else None
        rows_html += f"""
        <tr>
            <td>{e.component_name if e else ''}</td>
            <td style="text-align:right">{f'₹{e.amount:,.2f}' if e else ''}</td>
            <td>{d.component_name if d else ''}</td>
            <td style="text-align:right">{f'₹{d.amount:,.2f}' if d else ''}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Salary Slip — {slip.payroll_month}/{slip.payroll_year}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; font-size: 14px; }}
        h1 {{ margin: 0; color: #1a1a2e; }}
        h2 {{ color: #555; margin-top: 4px; }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #1a1a2e; padding-bottom: 12px; margin-bottom: 16px; }}
        .meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4px 24px; margin-bottom: 16px; }}
        .meta span {{ font-size: 13px; }} .meta b {{ color: #1a1a2e; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
        th {{ background: #1a1a2e; color: white; padding: 8px; text-align: left; }}
        td {{ padding: 7px 8px; border-bottom: 1px solid #eee; }}
        .total-row {{ background: #f0f4ff; font-weight: bold; }}
        .net-pay {{ margin-top: 16px; padding: 12px 16px; background: #1a1a2e; color: white; font-size: 18px; border-radius: 4px; }}
        .employer {{ margin-top: 8px; font-size: 12px; color: #888; }}
        @media print {{ button {{ display: none; }} }}
    </style>
</head>
<body>
    <div class="header">
        <div><h1>{co_name}</h1><h2>Salary Slip</h2></div>
        <div style="text-align:right">
            <div style="font-size:13px;color:#666">{slip.payroll_month:02d} / {slip.payroll_year}</div>
            <button onclick="window.print()" style="margin-top:8px;padding:6px 14px;cursor:pointer">🖨 Print / Save PDF</button>
        </div>
    </div>
    <div class="meta">
        <span><b>Employee:</b> {emp_name}</span>
        <span><b>Working Days:</b> {slip.working_days}</span>
        <span><b>Present Days:</b> {slip.present_days}</span>
        <span><b>LOP Days:</b> {slip.lop_days}</span>
    </div>
    <table>
        <thead><tr><th>Earnings</th><th style="text-align:right">Amount</th><th>Deductions</th><th style="text-align:right">Amount</th></tr></thead>
        <tbody>
            {rows_html}
            <tr class="total-row">
                <td>Gross Earnings</td><td style="text-align:right">₹{slip.gross_earnings:,.2f}</td>
                <td>Total Deductions</td><td style="text-align:right">₹{slip.total_deductions:,.2f}</td>
            </tr>
        </tbody>
    </table>
    <div class="net-pay">Net Pay: ₹{slip.net_pay:,.2f}</div>
    <div class="employer">Employer contributions — PF: ₹{slip.pf_employer:,.2f} &nbsp;|&nbsp; ESI: ₹{slip.esi_employer:,.2f}</div>
</body>
</html>"""

    return Response(content=html, media_type="text/html")


# ====== ROUTER 10: Reports ======

@finance_reports_router.get("/finance/reports/outstanding")
async def get_outstanding_report(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(
        Client.client_name,
        Invoice.invoice_number,
        Invoice.posting_date,
        Invoice.due_date,
        Invoice.total_amount,
        Invoice.amount_paid,
        Invoice.outstanding_amount
    ).join(Client).where(
        Invoice.tenant_id == current_user.tenant_id,
        Invoice.outstanding_amount > 0,
        Invoice.docstatus == 1
    )
    result = await db.execute(stmt)
    report = []
    for row in result.all():
        days_overdue = (date.today() - row.due_date).days if row.due_date and row.due_date < date.today() else 0
        report.append({
            "client_name": row.client_name,
            "invoice_number": row.invoice_number,
            "invoice_date": row.posting_date,
            "due_date": row.due_date,
            "total_amount": float(row.total_amount),
            "amount_paid": float(row.amount_paid),
            "outstanding": float(row.outstanding_amount),
            "days_overdue": days_overdue
        })
    return report

@finance_reports_router.get("/finance/reports/tds-summary")
async def get_tds_summary(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(
        Client.client_name,
        TDSConfig.section,
        TDSConfig.accumulated_payments_this_year,
        TDSConfig.rate
    ).join(TDSConfig, Client.id == TDSConfig.client_id).where(
        Client.tenant_id == current_user.tenant_id,
        TDSConfig.is_applicable == True
    )
    result = await db.execute(stmt)
    summary = []
    for row in result.all():
        tds_payable = float(row.accumulated_payments_this_year) * float(row.rate) / 100 if row.accumulated_payments_this_year else 0
        summary.append({
            "client_name": row.client_name,
            "tds_section": row.section,
            "total_payments_this_fy": float(row.accumulated_payments_this_year or 0),
            "tds_rate_percent": float(row.rate or 0),
            "estimated_tds_payable": round(tds_payable, 2)
        })
    return summary
