from typing import List, Optional, Literal
from uuid import UUID
from datetime import date, datetime, timezone
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
    PaymentBase, PaymentCreate, PaymentResponse,
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

# ====== ROUTER 1: Exchange Rate ======

@exchange_rate_router.post("/finance/exchange-rates/config", response_model=ExchangeRateConfigResponse, status_code=201)
async def upsert_exchange_rate_config(
    data: ExchangeRateConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "edit")
    
    # Check if exists
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
        config = ExchangeRateConfig(
            **data.model_dump(),
            tenant_id=current_user.tenant_id
        )
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
    await db.flush() # Get template.id
    
    for line_data in data.lines:
        line = TaxTemplateLine(
            **line_data.model_dump(),
            tax_template_id=template.id,
            tenant_id=current_user.tenant_id
        )
        db.add(line)
    
    await db.commit()
    
    # Reload with lines
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
    
    # Auto-create TDSConfig
    tds_data = data.tds_config.model_dump() if data.tds_config else {"is_applicable": False}
    tds_config = TDSConfig(
        **tds_data,
        client_id=client.id,
        tenant_id=current_user.tenant_id
    )
    db.add(tds_config)
    
    await db.commit()
    
    # Reload with TDS
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
    
    # Rules: Exchange rate fetch if needed
    if not quote.exchange_rate_locked:
        # TODO: Get base currency of company
        from app.modules.core_masters.models import Company
        stmt = select(Company).where(Company.id == quote.company_id)
        comp_res = await db.execute(stmt)
        company = comp_res.scalar_one()
        
        if company.base_currency_id and quote.currency_id and company.base_currency_id != quote.currency_id:
            from app.modules.core_masters.models import Currency
            stmt = select(Currency).where(Currency.id.in_([company.base_currency_id, quote.currency_id]))
            curr_res = await db.execute(stmt)
            currencies = {c.id: c.currency_code for c in curr_res.scalars()}
            
            rate_res = await fetch_exchange_rate(currencies[quote.currency_id], currencies[company.base_currency_id])
            if rate_res["success"]:
                quote.exchange_rate = Decimal(str(rate_res["rate"]))

    db.add(quote)
    await db.flush()
    
    # Add lines
    subtotal = Decimal("0")
    total_tax = Decimal("0")
    
    for line_data in data.line_items:
        # Note: In a real app, taxable_amount and tax_amount would be calculated here
        # based on rates and template lines provided or fetched.
        # For simplicity in this vertical slice, we'll assume the client sends pre-calculated totals
        # OR we'd call GSTCalculator here.
        
        line = QuoteLineItem(
            **line_data.model_dump(),
            quote_id=quote.id,
            tenant_id=current_user.tenant_id
        )
        # Recalculate if not provided (safety)
        line.taxable_amount = (line.quantity * line.rate * (1 - line.discount_percent/100)).quantize(Decimal("0.01"))
        
        # Simple tax calculation logic if template provided
        if line.tax_template_id:
            stmt = select(TaxTemplateLine).where(TaxTemplateLine.tax_template_id == line.tax_template_id)
            lines_res = await db.execute(stmt)
            template_lines = [{"rate": l.rate, "tax_name": l.tax_name} for l in lines_res.scalars()]
            
            # Fetch client/company states for GST
            stmt = select(Client).where(Client.id == quote.client_id)
            cl_res = await db.execute(stmt)
            client_obj = cl_res.scalar_one()
            
            stmt = select(Company).where(Company.id == quote.company_id)
            co_res = await db.execute(stmt)
            company_obj = co_res.scalar_one()
            
            gst_type = GSTCalculator.determine_gst_type(company_obj.state_code, client_obj.state_code, client_obj.country_code)
            tax_breakdown = GSTCalculator.calculate_line_tax(line.taxable_amount, template_lines, gst_type)
            line.tax_amount = tax_breakdown["total_tax"]
        
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

@quote_router.post("/finance/quotes/{id}/submit", response_model=QuoteResponse)
async def submit_quote(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "submit")
    stmt = select(Quote).where(Quote.id == id, Quote.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    quote = res.scalar_one()
    
    if quote.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only drafts can be submitted.")
    
    quote.docstatus = 1
    quote.status = "Sent"
    quote.quote_number = await get_next_number(db, current_user.tenant_id, quote.company_id, "QT", quote.posting_date)
    quote.exchange_rate_locked = True
    
    await db.commit()
    await db.refresh(quote)
    
    stmt = select(Quote).options(selectinload(Quote.line_items)).where(Quote.id == quote.id)
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
    
    # Auto due date
    if not invoice.due_date:
        stmt = select(Client).where(Client.id == invoice.client_id)
        cl_res = await db.execute(stmt)
        client = cl_res.scalar_one()
        from datetime import timedelta
        invoice.due_date = invoice.posting_date + timedelta(days=client.payment_terms_days)

    db.add(invoice)
    await db.flush()
    
    subtotal = Decimal("0")
    total_tax = Decimal("0")
    
    for line_data in data.line_items:
        line = InvoiceLineItem(
            **line_data.model_dump(),
            invoice_id=invoice.id,
            tenant_id=current_user.tenant_id
        )

        # Calculate taxable_amount (re-implementing for 100% certainty)
        line.taxable_amount = (
            line.quantity * line.rate * (1 - line.discount_percent / 100)
        ).quantize(Decimal("0.01"))

        # Calculate tax using GSTCalculator if template provided
        effective_template_id = line.tax_template_id or invoice.tax_template_id
        if effective_template_id:
            stmt = select(TaxTemplateLine).where(
                TaxTemplateLine.tax_template_id == effective_template_id
            )
            lines_res = await db.execute(stmt)
            template_lines = [
                {"rate": l.rate, "tax_name": l.tax_name}
                for l in lines_res.scalars()
            ]

            stmt = select(Client).where(Client.id == invoice.client_id)
            cl_res = await db.execute(stmt)
            client_obj = cl_res.scalar_one()

            from app.modules.core_masters.models import Company
            stmt = select(Company).where(Company.id == invoice.company_id)
            co_res = await db.execute(stmt)
            company_obj = co_res.scalar_one()

            gst_type = GSTCalculator.determine_gst_type(
                company_obj.state_code,
                client_obj.state_code,
                client_obj.country_code
            )
            tax_breakdown = GSTCalculator.calculate_line_tax(
                line.taxable_amount, template_lines, gst_type
            )
            line.tax_amount = tax_breakdown["total_tax"]
        else:
            line.tax_amount = Decimal("0")

        line.line_total = line.taxable_amount + line.tax_amount
        db.add(line)
        subtotal += line.taxable_amount
        total_tax += line.tax_amount

    # Update invoice totals
    invoice.subtotal = subtotal
    invoice.total_tax = total_tax
    invoice.total_amount = subtotal + total_tax
    invoice.outstanding_amount = invoice.total_amount
    invoice.base_total_amount = (invoice.total_amount * invoice.exchange_rate).quantize(Decimal("0.01"))
    
    await db.commit()
    
    stmt = select(Invoice).options(selectinload(Invoice.line_items), selectinload(Invoice.payments)).where(Invoice.id == invoice.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@invoice_router.post("/finance/invoices/{id}/submit", response_model=InvoiceResponse)
async def submit_invoice(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "submit")
    stmt = select(Invoice).where(Invoice.id == id, Invoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    invoice = res.scalar_one()
    
    if invoice.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only drafts can be submitted.")
    
    invoice.docstatus = 1
    invoice.status = "Sent"
    invoice.invoice_number = await get_next_number(db, current_user.tenant_id, invoice.company_id, "INV", invoice.posting_date)
    invoice.exchange_rate_locked = True
    
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
    invoice = res.scalar_one()
    
    if invoice.docstatus != 1:
        raise HTTPException(status_code=400, detail="Payments can only be added to submitted invoices.")

    # Record payment
    payment = Payment(
        **data.model_dump(),
        invoice_id=invoice.id,
        tenant_id=current_user.tenant_id
    )
    db.add(payment)
    
    # Rule 6: TDS Deduction Logic
    stmt = select(TDSConfig).where(TDSConfig.client_id == invoice.client_id)
    tds_res = await db.execute(stmt)
    tds_config = tds_res.scalar_one_or_none()
    
    if tds_config and tds_config.is_applicable:
        new_accumulated = tds_config.accumulated_payments_this_year + payment.amount_received
        if new_accumulated > tds_config.threshold_annual:
            # Note: prompt says tax applies to entire crossing payment
            payment.tds_deducted = (payment.amount_received * tds_config.rate / 100).quantize(Decimal("0.01"))
            payment.tds_section = tds_config.section
            tds_config.accumulated_payments_this_year = new_accumulated
            invoice.tds_amount += payment.tds_deducted

    # Rule 4: Atomic Update
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
        days_overdue = (date.today() - row.due_date).days if row.due_date < date.today() else 0
        report.append({
            "client_name": row.client_name,
            "invoice_number": row.invoice_number,
            "invoice_date": row.posting_date,
            "due_date": row.due_date,
            "total_amount": row.total_amount,
            "amount_paid": row.amount_paid,
            "outstanding": row.outstanding_amount,
            "days_overdue": days_overdue
        })
    return report

# ====== Stubs for remaining routers ======
# Implementations follow the same pattern as above.

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
        line = ProformaLineItem(
            **line_data.model_dump(),
            proforma_id=proforma.id,
            tenant_id=current_user.tenant_id
        )
        line.taxable_amount = (line.quantity * line.rate * (1 - line.discount_percent/100)).quantize(Decimal("0.01"))
        
        # GST Calculation (ensuring parity with Quote/Invoice)
        effective_template_id = line.tax_template_id or proforma.tax_template_id
        if effective_template_id:
            stmt = select(TaxTemplateLine).where(TaxTemplateLine.tax_template_id == effective_template_id)
            lines_res = await db.execute(stmt)
            template_lines = [{"rate": l.rate, "tax_name": l.tax_name} for l in lines_res.scalars()]
            
            stmt = select(Client).where(Client.id == proforma.client_id)
            cl_res = await db.execute(stmt)
            client_obj = cl_res.scalar_one()
            
            from app.modules.core_masters.models import Company
            stmt = select(Company).where(Company.id == proforma.company_id)
            co_res = await db.execute(stmt)
            company_obj = co_res.scalar_one()
            
            gst_type = GSTCalculator.determine_gst_type(company_obj.state_code, client_obj.state_code, client_obj.country_code)
            tax_breakdown = GSTCalculator.calculate_line_tax(line.taxable_amount, template_lines, gst_type)
            line.tax_amount = tax_breakdown["total_tax"]
        else:
            line.tax_amount = Decimal("0")
            
        line.line_total = line.taxable_amount + line.tax_amount
        db.add(line)
        subtotal += line.taxable_amount
        total_tax += line.tax_amount
        
    proforma.subtotal = subtotal
    proforma.total_tax = total_tax
    proforma.total_amount = subtotal + total_tax
    proforma.base_total_amount = (proforma.total_amount * proforma.exchange_rate).quantize(Decimal("0.01"))
    
    await db.commit()
    
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.id == proforma.id)
    result = await db.execute(stmt)
    return result.scalar_one()

@proforma_router.get("/finance/proforma-invoices/", response_model=List[ProformaResponse])
async def list_proformas(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(
        ProformaInvoice.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@proforma_router.get("/finance/proforma-invoices/{id}", response_model=ProformaResponse)
async def get_proforma(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(
        ProformaInvoice.id == id,
        ProformaInvoice.tenant_id == current_user.tenant_id
    )
    res = await db.execute(stmt)
    proforma = res.scalar_one_or_none()
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma invoice not found.")
    return proforma

@proforma_router.post("/finance/proforma-invoices/{id}/submit", response_model=ProformaResponse)
async def submit_proforma(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "submit")
    stmt = select(ProformaInvoice).where(ProformaInvoice.id == id, ProformaInvoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    proforma = res.scalar_one()
    
    if proforma.docstatus != 0:
        raise HTTPException(status_code=400, detail="Only drafts can be submitted.")
    
    proforma.docstatus = 1
    proforma.proforma_number = await get_next_number(db, current_user.tenant_id, proforma.company_id, "PI", proforma.posting_date)
    proforma.exchange_rate_locked = True
    
    await db.commit()
    
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.id == id)
    res = await db.execute(stmt)
    return res.scalar_one()

@proforma_router.post("/finance/proforma-invoices/{id}/cancel", response_model=ProformaResponse)
async def cancel_proforma(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "cancel")
    stmt = select(ProformaInvoice).where(ProformaInvoice.id == id, ProformaInvoice.tenant_id == current_user.tenant_id)
    res = await db.execute(stmt)
    proforma = res.scalar_one()
    
    if proforma.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only submitted invoices can be cancelled.")
    
    proforma.docstatus = 2
    proforma.status = "Cancelled"
    await db.commit()
    
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(ProformaInvoice.id == id)
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
    
    # Fetch proforma with line items
    stmt = select(ProformaInvoice).options(selectinload(ProformaInvoice.line_items)).where(
        ProformaInvoice.id == id,
        ProformaInvoice.tenant_id == current_user.tenant_id
    )
    res = await db.execute(stmt)
    proforma = res.scalar_one_or_none()
    
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma not found.")
    if proforma.docstatus != 1:
        raise HTTPException(status_code=400, detail="Only submitted proformas can be converted.")
    
    # Create Invoice
    invoice = Invoice(
        company_id=proforma.company_id,
        client_id=proforma.client_id,
        proforma_id=proforma.id,
        quote_id=proforma.quote_id,
        currency_id=proforma.currency_id,
        exchange_rate=proforma.exchange_rate,
        exchange_rate_locked=proforma.exchange_rate_locked,
        tax_template_id=proforma.tax_template_id,
        posting_date=data.posting_date,
        due_date=data.due_date,
        subtotal=proforma.subtotal,
        total_tax=proforma.total_tax,
        total_amount=proforma.total_amount,
        base_total_amount=proforma.base_total_amount,
        outstanding_amount=proforma.total_amount,
        notes=proforma.notes,
        terms=proforma.terms,
        tenant_id=current_user.tenant_id
    )
    db.add(invoice)
    await db.flush()
    
    # Copy lines
    for p_line in proforma.line_items:
        i_line = InvoiceLineItem(
            description=p_line.description,
            hsn_sac_code=p_line.hsn_sac_code,
            quantity=p_line.quantity,
            rate=p_line.rate,
            discount_percent=p_line.discount_percent,
            tax_template_id=p_line.tax_template_id,
            taxable_amount=p_line.taxable_amount,
            tax_amount=p_line.tax_amount,
            line_total=p_line.line_total,
            order_index=p_line.order_index,
            invoice_id=invoice.id,
            tenant_id=current_user.tenant_id
        )
        db.add(i_line)
    
    await db.commit()
    
    # Return with lines
    stmt = select(Invoice).options(selectinload(Invoice.line_items), selectinload(Invoice.payments)).where(Invoice.id == invoice.id)
    res = await db.execute(stmt)
    return res.scalar_one()

@recurring_router.post("/finance/recurring-invoices/", response_model=RecurringInvoiceConfigResponse, status_code=201)
async def create_recurring(
    data: RecurringInvoiceConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "create")

    # Verify template invoice exists and is submitted (docstatus=1)
    stmt = select(Invoice).where(
        Invoice.id == data.template_invoice_id,
        Invoice.tenant_id == current_user.tenant_id
    )
    res = await db.execute(stmt)
    template = res.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template invoice not found.")
    if template.docstatus != 1:
        raise HTTPException(
            status_code=400,
            detail="Template invoice must be submitted (docstatus=1) to be used for recurring setup."
        )

    config = RecurringInvoiceConfig(
        **data.model_dump(),
        tenant_id=current_user.tenant_id
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config

@recurring_router.get("/finance/recurring-invoices/", response_model=List[RecurringInvoiceConfigResponse])
async def list_recurring(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")
    stmt = select(RecurringInvoiceConfig).where(
        RecurringInvoiceConfig.tenant_id == current_user.tenant_id
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@recurring_router.patch("/finance/recurring-invoices/{id}", response_model=RecurringInvoiceConfigResponse)
async def patch_recurring(
    id: UUID,
    data: RecurringInvoiceConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "edit")
    stmt = select(RecurringInvoiceConfig).where(
        RecurringInvoiceConfig.id == id,
        RecurringInvoiceConfig.tenant_id == current_user.tenant_id
    )
    res = await db.execute(stmt)
    config = res.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found.")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    await db.commit()
    await db.refresh(config)
    return config

@recurring_router.post("/finance/recurring-invoices/{id}/pause", response_model=RecurringInvoiceConfigResponse)
async def pause_recurring(id: UUID, db: AsyncSession = Depends(get_db), cur: UserContext = Depends(get_current_user)):
    require_permission(cur, "finance", "edit")
    stmt = update(RecurringInvoiceConfig).where(
        RecurringInvoiceConfig.id == id,
        RecurringInvoiceConfig.tenant_id == cur.tenant_id
    ).values(is_active=False)
    await db.execute(stmt)
    await db.commit()
    res = await db.execute(select(RecurringInvoiceConfig).where(RecurringInvoiceConfig.id == id))
    return res.scalar_one()

@recurring_router.post("/finance/recurring-invoices/{id}/resume", response_model=RecurringInvoiceConfigResponse)
async def resume_recurring(id: UUID, db: AsyncSession = Depends(get_db), cur: UserContext = Depends(get_current_user)):
    require_permission(cur, "finance", "edit")
    stmt = update(RecurringInvoiceConfig).where(
        RecurringInvoiceConfig.id == id,
        RecurringInvoiceConfig.tenant_id == cur.tenant_id
    ).values(is_active=True)
    await db.execute(stmt)
    await db.commit()
    res = await db.execute(select(RecurringInvoiceConfig).where(RecurringInvoiceConfig.id == id))
    return res.scalar_one()

@salary_slip_html_router.get("/finance/salary-slips/{id}/html")
async def get_salary_slip_html(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user)
):
    require_permission(current_user, "finance", "view")

    # Import from payroll module — read only, never write
    from app.modules.payroll.models import SalarySlip, SalarySlipEarning, SalarySlipDeduction
    from app.modules.hr_masters.models import Employee
    from app.modules.core_masters.models import Company

    stmt = select(SalarySlip).options(
        selectinload(SalarySlip.earnings),
        selectinload(SalarySlip.deductions)
    ).where(
        SalarySlip.id == id,
        SalarySlip.tenant_id == current_user.tenant_id
    )
    res = await db.execute(stmt)
    slip = res.scalar_one_or_none()
    if not slip:
        raise HTTPException(status_code=404, detail="Salary slip not found.")

    # Fetch employee and company
    emp_stmt = select(Employee).where(Employee.id == slip.employee_id)
    emp_res = await db.execute(emp_stmt)
    employee = emp_res.scalar_one_or_none()

    co_stmt = select(Company).where(Company.id == slip.company_id)
    co_res = await db.execute(co_stmt)
    company = co_res.scalar_one_or_none()

    emp_name = employee.first_name + " " + employee.last_name if employee else "Unknown"
    co_name = company.company_name if company else "Unknown"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Salary Slip - {emp_name}</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 40px; color: #333; line-height: 1.5; }}
            h1 {{ color: #1a1a2e; margin-bottom: 4px; }}
            .sub-h {{ color: #666; font-size: 14px; margin-bottom: 24px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 16px; border: 1px solid #eee; }}
            th {{ background: #f8f9fa; text-align: left; padding: 12px; border-bottom: 2px solid #dee2e6; }}
            td {{ padding: 12px; border-bottom: 1px solid #eee; }}
            .total {{ font-weight: bold; background: #f8f9fa; }}
            .header {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #1a1a2e; padding-bottom: 16px; }}
            .net-pay {{ background: #1a1a2e; color: white; padding: 16px; border-radius: 4px; display: inline-block; margin-top: 24px; }}
            @media print {{ button {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>{co_name}</h1>
                <div class="sub-h">Official Salary Statement</div>
            </div>
            <div><button onclick="window.print()" style="padding: 8px 16px; cursor: pointer;">Print / Save PDF</button></div>
        </div>
        
        <div style="margin-top: 24px;">
            <div style="font-size: 20px; font-weight: bold;">Salary Slip — {slip.payroll_month}/{slip.payroll_year}</div>
            <p><strong>Employee:</strong> {emp_name}</p>
            <p><strong>Attendance:</strong> Working: {slip.working_days} | Present: {slip.present_days} | LOP: {slip.lop_days}</p>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Earnings</th>
                    <th>Amount (₹)</th>
                    <th>Deductions</th>
                    <th>Amount (₹)</th>
                </tr>
            </thead>
            <tbody>
    """

    earnings = slip.earnings or []
    deductions = slip.deductions or []
    max_rows = max(len(earnings), len(deductions))

    for i in range(max_rows):
        e = earnings[i] if i < len(earnings) else None
        d = deductions[i] if i < len(deductions) else None
        e_name = e.component_name if e else ""
        e_amt = f"{e.amount:,.2f}" if e else ""
        d_name = d.component_name if d else ""
        d_amt = f"{d.amount:,.2f}" if d else ""
        html += f"<tr><td>{e_name}</td><td>{e_amt}</td><td>{d_name}</td><td>{d_amt}</td></tr>"

    html += f"""
                <tr class="total">
                    <td>Gross Earnings</td>
                    <td>{slip.gross_earnings:,.2f}</td>
                    <td>Total Deductions</td>
                    <td>{slip.total_deductions:,.2f}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="net-pay">
            <span style="font-size: 14px; opacity: 0.8;">NET PAYABLE</span><br/>
            <span style="font-size: 24px; font-weight: bold;">₹{slip.net_pay:,.2f}</span>
        </div>

        <div style="margin-top: 24px; font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 16px;">
            <strong>Employer Contributions:</strong> 
            PF: ₹{slip.pf_employer:,.2f} | 
            ESI: ₹{slip.esi_employer:,.2f}
        </div>
    </body>
    </html>
    """

    return Response(content=html, media_type="text/html")
