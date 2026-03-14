# SKILL: Finance Module

## Module Overview
Location: `backend/app/modules/finance/`
RBAC: All endpoints require `require_permission(current_user, "finance", action)`
Roles with access: `owner`, `finance_manager`
Roles blocked: `hr_manager`, `manager`, `employee`, `auditor` (403 on all finance endpoints)

## Router Map
| Router prefix | Purpose |
|---|---|
| /api/finance/exchange-rates | Exchange rate config + live fetch |
| /api/finance/tax-templates | Tax template CRUD |
| /api/finance/clients | Client master + TDS config |
| /api/finance/quotes | Quote lifecycle |
| /api/finance/proforma-invoices | Proforma invoice lifecycle |
| /api/finance/invoices | Invoice lifecycle + payments |
| /api/finance/payments | Payment list + reversal |
| /api/finance/recurring-invoices | Recurring schedule management |
| /api/finance/salary-slips | HTML salary slip view (read-only) |
| /api/finance/reports | Outstanding + TDS summary |

## State Machines

### Quote
```
Draft (docstatus=0)
  → POST /{id}/submit   → Sent (docstatus=1, status="Sent")
                           quote_number assigned here (QT-2526-0001)
  → POST /{id}/accept   → Accepted (docstatus=1, status="Accepted")
  → POST /{id}/reject   → Rejected (docstatus=1, status="Rejected")
  → POST /{id}/cancel   → Cancelled (docstatus=2)
  → POST /{id}/convert-to-invoice   → Invoice created, status="Accepted"
  → POST /{id}/convert-to-proforma  → ProformaInvoice created
```

### Proforma Invoice
```
Draft (docstatus=0)
  → POST /{id}/submit   → Sent (docstatus=1)
                           proforma_number assigned here (PI-2526-0001)
  → POST /{id}/cancel   → Cancelled (docstatus=2)
  → POST /{id}/convert-to-invoice → Invoice created
```

### Invoice
```
Draft (docstatus=0)
  → POST /{id}/submit   → Sent (docstatus=1)
                           invoice_number assigned here (INV-2526-0001)
                           due_date set from posting_date + client.payment_terms_days
Sent (docstatus=1)
  → POST /{id}/payments → Partially Paid (status="Partially Paid")
  → POST /{id}/payments → Paid (status="Paid") when outstanding_amount <= 0
  → POST /{id}/cancel   → Cancelled (docstatus=2)
```

## Rule 1 — Never Hardcode Tax Rates
ALWAYS use TaxTemplate + TaxTemplateLine. Never write GST % directly
in business logic. Every line item references a tax_template_id.
The GSTCalculator reads template lines at calculation time.

```python
# CORRECT
gst_type = GSTCalculator.determine_gst_type(
    company.state_code, client.state_code, client.country_code
)
tax_result = GSTCalculator.calculate_line_tax(
    taxable_amount=line.taxable_amount,
    tax_template_lines=template_lines,
    gst_type=gst_type
)

# WRONG — never hardcode rates
cgst = taxable_amount * Decimal("0.09")
```

## Rule 2 — GST Type Determination
Always call GSTCalculator.determine_gst_type() before calculating.

```python
# Returns: "cgst_sgst" | "igst" | "export" | "none"
gst_type = GSTCalculator.determine_gst_type(
    company_state_code=company.state_code,   # e.g. "MH"
    client_state_code=client.state_code,     # e.g. "KA"
    client_country_code=client.country_code  # e.g. "IN"
)
# "export" and "none" → zero tax, no lines on invoice
```

## Rule 3 — Document Number Assignment
ONLY assign document numbers on submit (docstatus 0→1).
NEVER assign on create (draft). NEVER assign manually.

```python
# On submit endpoint — always use get_next_number():
invoice.invoice_number = await get_next_number(
    db, tenant_id, invoice.company_id, "INV", invoice.posting_date
)
# "QT" for quotes, "PI" for proformas
# Format: INV-2526-0001, QT-2526-0001, PI-2526-0001
```

## Rule 4 — Payment Updates Invoice Atomically
After every payment creation, update the parent invoice in the
SAME database transaction. outstanding_amount must never be stale.

```python
# In POST /invoices/{id}/payments endpoint:
invoice.amount_paid += payment.amount_received
invoice.outstanding_amount = invoice.total_amount - invoice.amount_paid
if invoice.outstanding_amount <= Decimal("0"):
    invoice.status = "Paid"
else:
    invoice.status = "Partially Paid"
# Commit invoice + payment together — never separately
await db.commit()
```

## Rule 5 — Exchange Rate Handling
```
On invoice/quote CREATE:
  If auto_fetch=True AND invoice_currency != company base_currency:
    Call fetch_exchange_rate() → pre-fill exchange_rate field
    Human can override before submit

On SUBMIT:
  Set exchange_rate_locked = True
  NEVER change exchange_rate after locked

Always store BOTH:
  total_amount      = amount in invoice currency
  base_total_amount = total_amount × exchange_rate (company reporting currency)
```

```python
if not quote.exchange_rate_locked:
    rate_data = await fetch_exchange_rate(
        from_currency=invoice_currency_code,
        to_currency=base_currency_code
    )
    if rate_data["success"]:
        quote.exchange_rate = Decimal(str(rate_data["rate"]))
```

## Rule 6 — TDS Deduction on Payment
Check TDSConfig before every payment. Only deduct when applicable
AND the annual threshold is crossed.

```python
tds_config = await get_tds_config(db, client_id, tenant_id)
if tds_config and tds_config.is_applicable:
    new_accumulated = (tds_config.accumulated_payments_this_year
                       + payment.amount_received)
    if new_accumulated > tds_config.threshold_annual:
        payment.tds_deducted = (
            payment.amount_received * tds_config.rate / 100
        ).quantize(Decimal("0.01"))
        payment.tds_section = tds_config.section
        tds_config.accumulated_payments_this_year = new_accumulated
        # Commit tds_config update in same transaction as payment
```

TDS rates by section:
- 194C_individual: 1.0%
- 194C_company: 2.0%
- 194J: 10.0%
- Threshold: ₹30,000 annual (default, configurable per client)

## Rule 7 — Salary Slip HTML is Read-Only
`GET /api/finance/salary-slips/{id}/html` reads from payroll module.
It NEVER writes to payroll tables.
Returns print-ready HTML for browser print dialog.
No WeasyPrint. No PDF generation. No new salary slip models.

## Rule 8 — Recurring Invoice Generation
When generating from RecurringInvoiceConfig:
1. Clone template_invoice → new Invoice (docstatus=0 or 1 based on auto_submit)
2. Set posting_date = today, due_date = today + client.payment_terms_days
3. Copy all InvoiceLineItems from template
4. Re-fetch exchange rate if auto_fetch=True
5. Calculate next_run_date based on frequency:
   - weekly: +7 days
   - monthly: +1 month (same day)
   - quarterly: +3 months
   - annual: +1 year
   - custom: +custom_interval_days
6. Update config: last_run_date=today, total_generated+=1, next_run_date=calculated

## Document Number Formats
| Document | Prefix | Example |
|---|---|---|
| Invoice | INV | INV-2526-0001 |
| Quote | QT | QT-2526-0001 |
| Proforma Invoice | PI | PI-2526-0001 |

Financial Year code: April→March
- 2026-03-14 → "2526" (FY 2025-26)
- 2026-04-01 → "2627" (FY 2026-27)
Numbering resets to 0001 at FY start, per company.

## Default Tax Templates (Pre-seeded)
| Template Name | Lines | Country |
|---|---|---|
| GST 18% Standard (IN) | CGST 9% + SGST 9% | IN |
| GST 12% (IN) | CGST 6% + SGST 6% | IN |
| GST 5% (IN) | CGST 2.5% + SGST 2.5% | IN |
| GST 0% / Exempt (IN) | 0% | IN |
| VAT 5% (AE) | VAT 5% | AE |
| Zero Rated Export | 0% | None (all countries) |

## Model → Table Reference
| Model | Table |
|---|---|
| ExchangeRateConfig | fin_exchange_rate_configs |
| TaxTemplate | fin_tax_templates |
| TaxTemplateLine | fin_tax_template_lines |
| Client | fin_clients |
| TDSConfig | fin_tds_configs |
| Quote | fin_quotes |
| QuoteLineItem | fin_quote_line_items |
| ProformaInvoice | fin_proforma_invoices |
| ProformaLineItem | fin_proforma_line_items |
| Invoice | fin_invoices |
| InvoiceLineItem | fin_invoice_line_items |
| Payment | fin_payments |
| RecurringInvoiceConfig | fin_recurring_invoice_configs |

## Key Utility Files
| File | Purpose |
|---|---|
| gst_calculator.py | Pure GST logic — no DB calls, fully testable |
| exchange_rate.py | exchangerate.host fetch + graceful fallback |
| invoice_numbering.py | get_next_number() — sequential per FY per company |
| seed_templates.py | Idempotent default tax template seeder |

## VEDA Integration (Task 3.4)
When building Finance Agent, always check permissions first:

```python
# In every finance agent tool:
if not check_permission(user, "finance", action):
    return make_blocker_response(
        reason=f"Your role ({user.role}) cannot access finance.",
        resolution_options=[],
        context=context
    )
```

Key tool → endpoint mappings:
- "Create quote for X" → POST /api/finance/quotes/
- "Convert to invoice" → POST /api/finance/quotes/{id}/convert-to-invoice
- "What's outstanding?" → GET /api/finance/reports/outstanding
- "X paid ₹Y against invoice Z" → POST /api/finance/invoices/{id}/payments
- "Create proforma for X" → POST /api/finance/proforma-invoices/
- "Set up monthly invoice for X" → POST /api/finance/recurring-invoices/
- "Show salary slip for Y" → GET /api/finance/salary-slips/{id}/html