import uuid
from datetime import datetime, date
from typing import Literal
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey, Numeric, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.modules.core_masters.models import CoreMasterBase

class ExchangeRateConfig(CoreMasterBase):
    __tablename__ = "fin_exchange_rate_configs"

    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False, unique=True)
    auto_fetch = Column(Boolean, default=True)
    api_provider = Column(String, default="exchangerate_host")

    # Relationships
    company = relationship("Company")

class TaxTemplate(CoreMasterBase):
    __tablename__ = "fin_tax_templates"

    template_name = Column(String, nullable=False)
    country_code = Column(String(2), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)

    # Relationships
    lines = relationship("TaxTemplateLine", back_populates="template", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'template_name', name='uq_fin_tax_template_name'),
    )

class TaxTemplateLine(CoreMasterBase):
    __tablename__ = "fin_tax_template_lines"

    tax_template_id = Column(UUID(as_uuid=True), ForeignKey("fin_tax_templates.id", ondelete="CASCADE"), nullable=False)
    tax_name = Column(String, nullable=False)
    rate = Column(Numeric(5, 2), nullable=False)
    is_inclusive = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)

    # Relationships
    template = relationship("TaxTemplate", back_populates="lines")

class Client(CoreMasterBase):
    __tablename__ = "fin_clients"

    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False)
    client_name = Column(String, nullable=False)
    gstin = Column(String(15), nullable=True)
    state_code = Column(String(2), nullable=True)
    country_code = Column(String(2), default="IN")
    currency_id = Column(UUID(as_uuid=True), ForeignKey("hr_currencies.id", ondelete="SET NULL"), nullable=True)
    billing_address = Column(Text, nullable=True)
    contact_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    pan_number = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    payment_terms_days = Column(Integer, default=30)

    # Relationships
    company = relationship("Company")
    currency = relationship("Currency")
    tds_config = relationship("TDSConfig", back_populates="client", uselist=False, cascade="all, delete-orphan")

class TDSConfig(CoreMasterBase):
    __tablename__ = "fin_tds_configs"

    client_id = Column(UUID(as_uuid=True), ForeignKey("fin_clients.id", ondelete="CASCADE"), nullable=False, unique=True)
    is_applicable = Column(Boolean, default=False)
    section = Column(String, nullable=True) # Literal["194C_individual", "194C_company", "194J"]
    rate = Column(Numeric(5, 2), nullable=True)
    threshold_annual = Column(Numeric(12, 2), default=30000.00)
    accumulated_payments_this_year = Column(Numeric(12, 2), default=0)

    # Relationships
    client = relationship("Client", back_populates="tds_config")

class Quote(CoreMasterBase):
    __tablename__ = "fin_quotes"

    docstatus = Column(Integer, default=0)
    status = Column(String, default="Draft")
    quote_number = Column(String, nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("fin_clients.id", ondelete="RESTRICT"), nullable=False)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("hr_currencies.id", ondelete="SET NULL"), nullable=True)
    exchange_rate = Column(Numeric(18, 6), default=1.000000)
    exchange_rate_locked = Column(Boolean, default=False)
    tax_template_id = Column(UUID(as_uuid=True), ForeignKey("fin_tax_templates.id", ondelete="SET NULL"), nullable=True)
    subtotal = Column(Numeric(18, 2), default=0)
    total_tax = Column(Numeric(18, 2), default=0)
    total_amount = Column(Numeric(18, 2), default=0)
    base_total_amount = Column(Numeric(18, 2), default=0)
    valid_until = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    posting_date = Column(Date, nullable=False)

    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    currency = relationship("Currency")
    tax_template = relationship("TaxTemplate")
    line_items = relationship("QuoteLineItem", back_populates="parent", cascade="all, delete-orphan")

class QuoteLineItem(CoreMasterBase):
    __tablename__ = "fin_quote_line_items"

    quote_id = Column(UUID(as_uuid=True), ForeignKey("fin_quotes.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    hsn_sac_code = Column(String(8), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    rate = Column(Numeric(18, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    taxable_amount = Column(Numeric(18, 2), nullable=False)
    tax_template_id = Column(UUID(as_uuid=True), ForeignKey("fin_tax_templates.id", ondelete="SET NULL"), nullable=True)
    tax_amount = Column(Numeric(18, 2), default=0)
    line_total = Column(Numeric(18, 2), nullable=False)
    order_index = Column(Integer, default=0)

    # Relationships
    parent = relationship("Quote", back_populates="line_items")
    tax_template = relationship("TaxTemplate")

class ProformaInvoice(CoreMasterBase):
    __tablename__ = "fin_proforma_invoices"

    docstatus = Column(Integer, default=0)
    status = Column(String, default="Draft")
    proforma_number = Column(String, nullable=True) # WATCH POINT 2: proforma_number
    quote_id = Column(UUID(as_uuid=True), ForeignKey("fin_quotes.id", ondelete="SET NULL"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("fin_clients.id", ondelete="RESTRICT"), nullable=False)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("hr_currencies.id", ondelete="SET NULL"), nullable=True)
    exchange_rate = Column(Numeric(18, 6), default=1.000000)
    exchange_rate_locked = Column(Boolean, default=False)
    tax_template_id = Column(UUID(as_uuid=True), ForeignKey("fin_tax_templates.id", ondelete="SET NULL"), nullable=True)
    subtotal = Column(Numeric(18, 2), default=0)
    total_tax = Column(Numeric(18, 2), default=0)
    total_amount = Column(Numeric(18, 2), default=0)
    base_total_amount = Column(Numeric(18, 2), default=0)
    valid_until = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    posting_date = Column(Date, nullable=False)

    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    currency = relationship("Currency")
    tax_template = relationship("TaxTemplate")
    line_items = relationship("ProformaLineItem", back_populates="parent", cascade="all, delete-orphan")
    quote = relationship("Quote")

class ProformaLineItem(CoreMasterBase):
    __tablename__ = "fin_proforma_line_items"

    proforma_id = Column(UUID(as_uuid=True), ForeignKey("fin_proforma_invoices.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    hsn_sac_code = Column(String(8), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    rate = Column(Numeric(18, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    taxable_amount = Column(Numeric(18, 2), nullable=False)
    tax_template_id = Column(UUID(as_uuid=True), ForeignKey("fin_tax_templates.id", ondelete="SET NULL"), nullable=True)
    tax_amount = Column(Numeric(18, 2), default=0)
    line_total = Column(Numeric(18, 2), nullable=False)
    order_index = Column(Integer, default=0)

    # Relationships
    parent = relationship("ProformaInvoice", back_populates="line_items")
    tax_template = relationship("TaxTemplate")

class Invoice(CoreMasterBase):
    __tablename__ = "fin_invoices"

    docstatus = Column(Integer, default=0)
    status = Column(String, default="Draft")
    invoice_number = Column(String, nullable=True)
    quote_id = Column(UUID(as_uuid=True), ForeignKey("fin_quotes.id", ondelete="SET NULL"), nullable=True)
    proforma_id = Column(UUID(as_uuid=True), ForeignKey("fin_proforma_invoices.id", ondelete="SET NULL"), nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("hr_companies.id", ondelete="RESTRICT"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("fin_clients.id", ondelete="RESTRICT"), nullable=False)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("hr_currencies.id", ondelete="SET NULL"), nullable=True)
    exchange_rate = Column(Numeric(18, 6), default=1.000000)
    exchange_rate_locked = Column(Boolean, default=False)
    tax_template_id = Column(UUID(as_uuid=True), ForeignKey("fin_tax_templates.id", ondelete="SET NULL"), nullable=True)
    subtotal = Column(Numeric(18, 2), default=0)
    total_tax = Column(Numeric(18, 2), default=0)
    total_amount = Column(Numeric(18, 2), default=0)
    base_total_amount = Column(Numeric(18, 2), default=0)
    due_date = Column(Date, nullable=True)
    posting_date = Column(Date, nullable=False)
    amount_paid = Column(Numeric(18, 2), default=0)
    outstanding_amount = Column(Numeric(18, 2), default=0)
    tds_amount = Column(Numeric(18, 2), default=0)
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)

    # Relationships
    company = relationship("Company")
    client = relationship("Client")
    currency = relationship("Currency")
    tax_template = relationship("TaxTemplate")
    line_items = relationship("InvoiceLineItem", back_populates="parent", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")
    quote = relationship("Quote")
    proforma = relationship("ProformaInvoice")

class InvoiceLineItem(CoreMasterBase):
    __tablename__ = "fin_invoice_line_items"

    invoice_id = Column(UUID(as_uuid=True), ForeignKey("fin_invoices.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    hsn_sac_code = Column(String(8), nullable=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    rate = Column(Numeric(18, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    taxable_amount = Column(Numeric(18, 2), nullable=False)
    tax_template_id = Column(UUID(as_uuid=True), ForeignKey("fin_tax_templates.id", ondelete="SET NULL"), nullable=True)
    tax_amount = Column(Numeric(18, 2), default=0)
    line_total = Column(Numeric(18, 2), nullable=False)
    order_index = Column(Integer, default=0)

    # Relationships
    parent = relationship("Invoice", back_populates="line_items")
    tax_template = relationship("TaxTemplate")

class Payment(CoreMasterBase):
    __tablename__ = "fin_payments"

    invoice_id = Column(UUID(as_uuid=True), ForeignKey("fin_invoices.id", ondelete="RESTRICT"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount_received = Column(Numeric(18, 2), nullable=False)
    payment_mode = Column(String, nullable=False) # Literal["bank_transfer", "cheque", "cash", "upi", "card", "other"]
    reference_number = Column(String, nullable=True)
    tds_deducted = Column(Numeric(18, 2), default=0)
    tds_section = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    exchange_rate_at_payment = Column(Numeric(18, 6), default=1.000000)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")

class RecurringInvoiceConfig(CoreMasterBase):
    __tablename__ = "fin_recurring_invoice_configs"

    template_invoice_id = Column(UUID(as_uuid=True), ForeignKey("fin_invoices.id", ondelete="RESTRICT"), nullable=False)
    frequency = Column(String, nullable=False) # Literal["weekly", "monthly", "quarterly", "annual", "custom"]
    custom_interval_days = Column(Integer, nullable=True)
    next_run_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    auto_submit = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_run_date = Column(Date, nullable=True)
    total_generated = Column(Integer, default=0)

    # Relationships
    template_invoice = relationship("Invoice")
