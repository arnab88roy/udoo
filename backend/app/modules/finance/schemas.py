from typing import Optional, List, Literal, Union
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from app.modules.core_masters.schemas import CoreMasterSchemaBase, CoreMasterSchemaResponse

# ====== ExchangeRateConfig ======
class ExchangeRateConfigBase(BaseModel):
    company_id: UUID = Field(..., description="Which company this config belongs to.")
    auto_fetch: bool = Field(True, description="If True, fetch rate from exchangerate.host on invoice creation.")
    api_provider: str = Field("exchangerate_host", description="Exchange rate provider.")

class ExchangeRateConfigCreate(ExchangeRateConfigBase):
    pass

class ExchangeRateConfigResponse(ExchangeRateConfigBase, CoreMasterSchemaResponse):
    pass

# ====== TaxTemplate & Lines ======
class TaxTemplateLineBase(BaseModel):
    tax_name: str = Field(..., description="Tax component name. e.g. 'CGST', 'SGST', 'IGST'.")
    rate: Decimal = Field(..., description="Tax rate as percentage. e.g. 9.00 for 9%.")
    is_inclusive: bool = Field(False, description="If True, tax is included in the line item rate.")
    order_index: int = Field(0, description="Display order of tax lines.")

class TaxTemplateLineCreate(TaxTemplateLineBase):
    pass

class TaxTemplateLineResponse(TaxTemplateLineBase, CoreMasterSchemaResponse):
    tax_template_id: UUID

class TaxTemplateBase(BaseModel):
    template_name: str = Field(..., description="Display name. e.g. 'GST 18% Standard'.")
    country_code: Optional[str] = Field(None, description="ISO 2-letter country code. Null = all countries.")
    description: Optional[str] = Field(None, description="Template description.")
    is_active: bool = Field(True, description="Whether this template is available for use.")

class TaxTemplateCreate(TaxTemplateBase):
    lines: List[TaxTemplateLineCreate] = Field(..., description="Tax component lines.")

class TaxTemplateResponse(TaxTemplateBase, CoreMasterSchemaResponse):
    lines: List[TaxTemplateLineResponse]

# ====== Client & TDSConfig ======
class TDSConfigBase(BaseModel):
    is_applicable: bool = Field(False, description="Whether TDS is deducted on payments.")
    section: Optional[Literal["194C_individual", "194C_company", "194J"]] = Field(None, description="TDS section code.")
    rate: Optional[Decimal] = Field(None, description="TDS deduction rate as percentage.")
    threshold_annual: Decimal = Field(30000.00, description="Annual payment threshold (default ₹30k).")

class TDSConfigCreate(TDSConfigBase):
    pass

class TDSConfigUpdate(TDSConfigBase):
    pass

class TDSConfigResponse(TDSConfigBase, CoreMasterSchemaResponse):
    client_id: UUID
    accumulated_payments_this_year: Decimal

class ClientBase(BaseModel):
    company_id: UUID = Field(..., description="Which company this client belongs to.")
    client_name: str = Field(..., description="Display name of the client.")
    gstin: Optional[str] = Field(None, description="Client's GSTIN for Indian GST invoicing.")
    state_code: Optional[str] = Field(None, description="Client's state code for GST type determination.")
    country_code: str = Field("IN", description="ISO 2-letter country code.")
    currency_id: Optional[UUID] = Field(None, description="Client's preferred invoice currency.")
    billing_address: Optional[str] = Field(None, description="Detailed billing address.")
    contact_name: Optional[str] = Field(None, description="Primary contact person.")
    contact_email: Optional[str] = Field(None, description="Primary contact email.")
    contact_phone: Optional[str] = Field(None, description="Primary contact phone.")
    pan_number: Optional[str] = Field(None, description="Client's PAN for TDS deduction.")
    is_active: bool = Field(True, description="Whether this client is active.")
    payment_terms_days: int = Field(30, description="Default payment terms in days.")

class ClientCreate(ClientBase):
    tds_config: Optional[TDSConfigCreate] = None

class ClientUpdate(BaseModel):
    client_name: Optional[str] = None
    gstin: Optional[str] = None
    state_code: Optional[str] = None
    country_code: Optional[str] = None
    currency_id: Optional[UUID] = None
    billing_address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    pan_number: Optional[str] = None
    is_active: Optional[bool] = None
    payment_terms_days: Optional[int] = None

class ClientResponse(ClientBase, CoreMasterSchemaResponse):
    tds_config: Optional[TDSConfigResponse] = None

# ====== Common Transactional Schemas ======
class LineItemBase(BaseModel):
    description: str = Field(..., description="Line item description.")
    hsn_sac_code: Optional[str] = Field(None, description="HSN/SAC code for GST compliance.")
    quantity: Decimal = Field(..., description="Quantity of items.")
    rate: Decimal = Field(..., description="Rate per unit in invoice currency.")
    discount_percent: Decimal = Field(0, description="Line item discount percent.")
    tax_template_id: Optional[UUID] = Field(None, description="Tax template for this specific line.")
    order_index: int = Field(0, description="Display order.")

class LineItemResponseBase(LineItemBase, CoreMasterSchemaResponse):
    taxable_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal

class TransactionBase(BaseModel):
    company_id: UUID = Field(..., description="Issuing company.")
    client_id: UUID = Field(..., description="Draft client.")
    currency_id: Optional[UUID] = Field(None, description="Invoice currency.")
    exchange_rate: Decimal = Field(1.0, description="Conversion rate to base currency.")
    exchange_rate_locked: bool = Field(False, description="Whether rate is manual/locked.")
    tax_template_id: Optional[UUID] = Field(None, description="Default tax template for all lines.")
    posting_date: date = Field(..., description="Document date.")
    notes: Optional[str] = Field(None, description="Public notes.")
    terms: Optional[str] = Field(None, description="Terms and conditions.")

class TransactionResponseBase(TransactionBase, CoreMasterSchemaResponse):
    docstatus: int
    status: str
    subtotal: Decimal
    total_tax: Decimal
    total_amount: Decimal
    base_total_amount: Decimal

# ====== Quote ======
class QuoteLineItemCreate(LineItemBase):
    pass

class QuoteLineItemResponse(LineItemResponseBase):
    quote_id: UUID

class QuoteCreate(TransactionBase):
    valid_until: Optional[date] = Field(None, description="Quote expiry date.")
    line_items: List[QuoteLineItemCreate] = Field(..., description="Line items for this quote.")

class QuoteUpdate(BaseModel):
    client_id: Optional[UUID] = None
    currency_id: Optional[UUID] = None
    posting_date: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    terms: Optional[str] = None

class QuoteResponse(TransactionResponseBase):
    quote_number: Optional[str] = None
    valid_until: Optional[date] = None
    line_items: List[QuoteLineItemResponse]

# ====== Proforma Invoice ======
class ProformaLineItemCreate(LineItemBase):
    pass

class ProformaLineItemResponse(LineItemResponseBase):
    proforma_id: UUID

class ProformaCreate(TransactionBase):
    quote_id: Optional[UUID] = None
    valid_until: Optional[date] = None
    line_items: List[ProformaLineItemCreate]

class ProformaResponse(TransactionResponseBase):
    proforma_number: Optional[str] = None # WATCH POINT 2
    quote_id: Optional[UUID] = None
    valid_until: Optional[date] = None
    line_items: List[ProformaLineItemResponse]

# ====== Invoice & Payment ======
class InvoiceLineItemCreate(LineItemBase):
    pass

class InvoiceLineItemResponse(LineItemResponseBase):
    invoice_id: UUID

class PaymentBase(BaseModel):
    payment_date: date = Field(..., description="Date payment was received.")
    amount_received: Decimal = Field(..., description="Amount received in invoice currency.")
    payment_mode: Literal["bank_transfer", "cheque", "cash", "upi", "card", "other"] = Field(..., description="Payment method.")
    reference_number: Optional[str] = Field(None, description="Transaction ID/Check number.")
    tds_deducted: Decimal = Field(0, description="TDS amount deducted by client.")
    tds_section: Optional[str] = Field(None, description="TDS section applied.")
    notes: Optional[str] = Field(None, description="Internal notes.")

class PaymentCreate(PaymentBase):
    invoice_id: UUID

class PaymentResponse(PaymentBase, CoreMasterSchemaResponse):
    exchange_rate_at_payment: Decimal

class InvoiceCreate(TransactionBase):
    quote_id: Optional[UUID] = None
    proforma_id: Optional[UUID] = None
    due_date: Optional[date] = Field(None, description="Payment due date.")
    line_items: List[InvoiceLineItemCreate]

class InvoiceUpdate(BaseModel):
    due_date: Optional[date] = None
    notes: Optional[str] = None
    terms: Optional[str] = None

class InvoiceResponse(TransactionResponseBase):
    invoice_number: Optional[str] = None
    due_date: Optional[date] = None
    amount_paid: Decimal
    outstanding_amount: Decimal
    tds_amount: Decimal
    quote_id: Optional[UUID] = None
    proforma_id: Optional[UUID] = None
    line_items: List[InvoiceLineItemResponse]
    payments: List[PaymentResponse]

# ====== RecurringInvoiceConfig ======
class RecurringInvoiceConfigBase(BaseModel):
    template_invoice_id: UUID = Field(..., description="Submitted invoice to use as template.")
    frequency: Literal["weekly", "monthly", "quarterly", "annual", "custom"] = Field(..., description="Recurrence frequency.")
    custom_interval_days: Optional[int] = Field(None, description="Interval in days for frequency='custom'.")
    next_run_date: date = Field(..., description="Next date to generate invoice.")
    end_date: Optional[date] = Field(None, description="Optional stop date.")
    auto_submit: bool = Field(False, description="If True, auto-submit generated invoice.")
    is_active: bool = Field(True, description="Toggle recurrence.")

class RecurringInvoiceConfigCreate(RecurringInvoiceConfigBase):
    pass

class RecurringInvoiceConfigUpdate(BaseModel):
    frequency: Optional[str] = None
    next_run_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None

class RecurringInvoiceConfigResponse(RecurringInvoiceConfigBase, CoreMasterSchemaResponse):
    last_run_date: Optional[date] = None
    total_generated: int

# ====== Action Request Schemas ======
class ConvertToInvoiceRequest(BaseModel):
    posting_date: date = Field(..., description="Invoice posting date.")
    due_date: Optional[date] = Field(None, description="Force a specific due date.")

class FetchExchangeRateRequest(BaseModel):
    from_currency: str = Field(..., description="3-letter currency code. e.g. USD")
    to_currency: str = Field(..., description="3-letter currency code. e.g. INR")

class FetchExchangeRateResponse(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    fetched_at: datetime
    source: str = "exchangerate_host"
    success: bool
    error: Optional[str] = None
