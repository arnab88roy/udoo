# VEDA Capabilities Registry
## What VEDA Can Do — Udoo ERP

> **Reading guide:** This document is written from the user's perspective.
> Every line is something a real user would say or ask.
> Status markers: ✅ Live | 🔄 In Development | 📋 Planned | 🔭 Future Scope | ❌ Out of Scope

---

## How to Read This Document

VEDA operates across three modes:

**Ask** — retrieve and display information
**Act** — execute a business operation
**Advise** — proactively surface insights, anomalies, or recommendations

Most competitors stop at Ask. VEDA is built to Act and Advise.

---

## MODULE 1: People & HR

### Employee Management
| What the user says | What VEDA does | Status |
|---|---|---|
| "Show me all active employees" | Lists employees with role-scoped filtering | ✅ Live |
| "Show me inactive employees" | Lists with status filter | ✅ Live |
| "Show me details for Priya Sharma" | Fetches employee record as inline FORM card | ✅ Live |
| "Add a new employee" | Opens pre-filled creation form inline | 📋 Planned (Task 3.2 form tools) |
| "Update Rahul's designation to Senior Engineer" | VEDA edits the field with purple attribution | 📋 Planned |
| "Who reports to Ankit?" | Queries reporting chain | 📋 Planned |
| "Show me employees joining this month" | Filters by date_of_joining | 📋 Planned |
| "Who hasn't confirmed their bank account yet?" | Queries incomplete profiles | 🔭 Future Scope |
| "Flag employees whose contracts end this quarter" | Proactive contract expiry alert | 🔭 Future Scope |

### Leave Management
| What the user says | What VEDA does | Status |
|---|---|---|
| "Show me pending leave approvals" | Lists submitted-open leaves for manager's team | ✅ Live |
| "Show me approved leaves this month" | Filters by status | ✅ Live |
| "Approve Dev's leave" | Shows APPROVAL card → human confirms → DB updates | ✅ Live |
| "Reject Rahul's leave request" | Shows APPROVAL card with Reject action | ✅ Live |
| "Apply for leave from March 20 to March 25" | Creates leave application for current employee | 📋 Planned |
| "How many casual leaves do I have left?" | Queries leave balance for employee | 📋 Planned |
| "Show team leave calendar for April" | Visual leave summary by date | 🔭 Future Scope |
| "Who is on leave today?" | Real-time team leave status | 🔭 Future Scope |
| "Alert me when more than 3 people in engineering are on leave simultaneously" | Policy-driven proactive alert | 🔭 Future Scope |

### Attendance Management
| What the user says | What VEDA does | Status |
|---|---|---|
| "Show my attendance summary for last 30 days" | Aggregated attendance by status | ✅ Live |
| "Show team attendance for this week" | Manager-scoped attendance summary | ✅ Live |
| "Mark today's attendance for field team" | Bulk attendance entry | 📋 Planned |
| "Who was absent yesterday?" | Absence query with org scope | 📋 Planned |
| "Show late arrivals this month" | Filters on late_entry flag | 📋 Planned |
| "Approve Meera's attendance correction request" | AttendanceRequest approval flow | 📋 Planned |
| "Flag employees with more than 3 unexcused absences this month" | Anomaly detection | 🔭 Future Scope |
| "Sync biometric device data and reconcile attendance" | Biometric integration | 🔭 Future Scope |

---

## MODULE 2: Payroll

### Salary Operations
| What the user says | What VEDA does | Status |
|---|---|---|
| "Run payroll for March 2026" | PROGRESS → CONFIRM → bulk salary slip generation | 📋 Planned (Task 3.3) |
| "Show payroll status for this month" | Summary of generated/pending slips | 📋 Planned (Task 3.3) |
| "Show Priya's salary slip for February" | Fetches slip as FORM UIResponse | 📋 Planned (Task 3.3) |
| "What is Dev's net pay this month?" | Single employee payroll query | 📋 Planned (Task 3.3) |
| "Submit payroll for March" | CONFIRM → submits all slips | 📋 Planned (Task 3.3) |
| "Show me the PF deduction summary for March" | Compliance summary | 📋 Planned (Task 3.3) |
| "Generate bank transfer file for this month's payroll" | Bank disbursement file export | 🔭 Future Scope (Phase 5) |
| "Generate Form 16 for all employees" | Annual tax certificate generation | 🔭 Future Scope (Phase 5) |
| "Process full and final settlement for Rahul who resigned" | F&F calculation under new Labour Code 2025 | 🔭 Future Scope (Phase 5) |

### Indian Compliance — Payroll
| What the user says | What VEDA does | Status |
|---|---|---|
| "Is our basic salary structure compliant with the new 50% wage rule?" | Checks CTC structure against November 2025 Labour Code | 🔭 Future Scope |
| "Which employees cross the ESI ceiling this month?" | ESI eligibility monitoring | 📋 Planned (Task 3.3) |
| "Show me PF contribution summary for EPFO filing" | Monthly PF report | 🔭 Future Scope (Phase 5) |
| "What's our TDS liability for this quarter?" | TDS aggregation across all employees | 🔭 Future Scope (Phase 5) |
| "Alert me 3 days before PF filing deadline" | Proactive compliance reminder | 🔭 Future Scope |
| "Generate Form 24Q for Q4" | Quarterly TDS return | 🔭 Future Scope (Phase 5) |
| "Check if any employee needs gratuity calculation — they complete 1 year next month" | Gratuity eligibility under new Social Security Code | 🔭 Future Scope |

---

## MODULE 3: Finance

### Invoicing & Quotes
| What the user says | What VEDA does | Status |
|---|---|---|
| "Create a quote for Sharma Textiles for 5 days consulting at ₹15,000/day" | Pre-fills FORM with GST auto-calculated | 📋 Planned (Task 3.4) |
| "Convert that quote to an invoice" | Quote → Invoice state transition | 📋 Planned (Task 3.4) |
| "Show me all outstanding invoices" | TABLE with outstanding amounts | 📋 Planned (Task 3.4) |
| "What's my total receivable this month?" | Aggregated finance query | 📋 Planned (Task 3.4) |
| "Sharma Textiles paid ₹45,000 against invoice INV-2526-004" | Records payment, updates outstanding | 📋 Planned (Task 3.4) |
| "Mark invoice INV-2526-007 as sent" | State machine transition | 📋 Planned (Task 3.4) |
| "Show me overdue invoices older than 30 days" | Filtered invoice query | 📋 Planned (Task 3.4) |
| "Send a payment reminder to all clients with invoices overdue by 15+ days" | Bulk client communication | 🔭 Future Scope |
| "What's my GST liability for this quarter?" | CGST/SGST/IGST aggregation | 🔭 Future Scope (Phase 5) |
| "Generate GSTR-1 summary for March" | GST return preparation | 🔭 Future Scope (Phase 5) |

### Client Management
| What the user says | What VEDA does | Status |
|---|---|---|
| "Add a new client — Mehta Industries, GSTIN 27AAAAA0000A1Z5" | Creates client master with GST validation | 📋 Planned (Task 3.4) |
| "Show me all clients" | Client list | 📋 Planned (Task 3.4) |
| "What's Sharma Textiles' total billing this year?" | Client-level revenue query | 🔭 Future Scope |
| "Which clients haven't been invoiced in 60 days?" | Lapsed client detection | 🔭 Future Scope |

---

## MODULE 4: Setup & Company Configuration

### Onboarding
| What the user says | What VEDA does | Status |
|---|---|---|
| "Set up my company" | 5-question onboarding conversation | 📋 Planned (Task 3.6) |
| "Add a new department called Product" | Creates department master | 📋 Planned (Task 3.6) |
| "Add a designation — Senior Engineer" | Creates designation master | 📋 Planned (Task 3.6) |
| "Set up our leave policy — 12 casual leaves, 12 earned leaves per year" | Configures leave types | 📋 Planned (Task 3.6) |
| "Set our payroll run date to the 28th of every month" | Policy engine configuration | 📋 Planned (Task 3.5) |
| "Require manager approval for leaves longer than 3 days" | Approval threshold policy | 📋 Planned (Task 3.5) |

---

## MODULE 5: Intelligence & Insights

*This is where VEDA diverges from all existing competitors.
Every insight below is grounded in the company's actual live data — not generic benchmarks.*

### Business Intelligence
| What the user says | What VEDA does | Status |
|---|---|---|
| "What's my headcount trend over the last 6 months?" | Queries employee records by joining date | 🔭 Future Scope |
| "What's my monthly payroll cost trend?" | Aggregates salary slips over time | 🔭 Future Scope |
| "Which department has the highest leave utilisation?" | Cross-department leave analysis | 🔭 Future Scope |
| "What's my revenue per employee this quarter?" | Finance ÷ Headcount calculation | 🔭 Future Scope |
| "Show me attrition risk — who hasn't had a salary revision in 18 months?" | Proactive retention insight | 🔭 Future Scope |

### Proactive Alerts (VEDA speaks first, without being asked)
| VEDA proactively says... | Trigger condition | Status |
|---|---|---|
| "Payroll for March is due in 3 days. 2 employees have missing bank accounts." | Payroll run date from policy engine | 🔭 Future Scope |
| "You have 4 pending leave approvals. Oldest is 5 days old." | On login, for managers | 📋 Planned (Task 3.7) |
| "ESI filing deadline is in 2 days." | Compliance calendar | 🔭 Future Scope |
| "Rahul Singh's contract ends in 30 days. No renewal has been initiated." | Contract expiry monitoring | 🔭 Future Scope |
| "3 invoices totalling ₹2.4L are overdue by 30+ days." | On login, for finance managers | 📋 Planned (Task 3.7) |
| "Your basic salary structure may not comply with the new 50% wage rule for 6 employees." | Labour Code 2025 compliance check | 🔭 Future Scope |

---

## MODULE 6: Reports & Documents

*VEDA's reports are different from generic AI document tools.
Every output is generated from live database data — not a template.*

### Data-Grounded Reports
| What the user says | What VEDA does | Status |
|---|---|---|
| "Generate a monthly HR summary report" | Headcount, leaves, attendance from live DB | 🔭 Future Scope (Phase 5) |
| "Generate our org chart" | Mermaid diagram from actual reporting hierarchy | 🔭 Future Scope (Phase 5) |
| "Create a payroll summary PDF for the board" | PDF from actual salary slip data | 🔭 Future Scope (Phase 5) |
| "Export payslips for all employees as PDFs" | Bulk payslip generation | 🔭 Future Scope (Phase 5) |
| "Generate an onboarding document for our 3 new joiners next Monday" | Personalised doc using actual employee records | 🔭 Future Scope (Phase 5) |
| "Show me a cash flow forecast for next quarter" | Finance data + trend extrapolation | 🔭 Future Scope |

---

## MODULE 7: Communication & Integrations

### WhatsApp (Critical for Indian SME retention)
| What the user says | What VEDA does | Status |
|---|---|---|
| "Send payslips to all employees via WhatsApp" | WhatsApp delivery of salary slips | 🔭 Future Scope (Phase 5) |
| "Send a leave approval notification to Dev on WhatsApp" | HITL action → WhatsApp notification | 🔭 Future Scope (Phase 5) |
| "Allow employees to apply for leave via WhatsApp" | WhatsApp as input channel | 🔭 Future Scope (Phase 5) |

### Self-Service (Employee Portal)
| What the user says | What VEDA does | Status |
|---|---|---|
| "What can I do?" | Describes current user's permissions | ✅ Live |
| "Show my payslip for February" | Employee fetches own salary slip | 📋 Planned (Task 3.3) |
| "Apply for casual leave next Friday" | Employee creates own leave application | 📋 Planned |
| "Download my Form 16" | Employee fetches own tax certificate | 🔭 Future Scope (Phase 5) |
| "What's my leave balance?" | Employee queries own leave data | 📋 Planned |

---

## What VEDA Will Never Do

These are explicit non-goals. Being clear about this is as important as the capabilities list.

| Capability | Why it's out of scope |
|---|---|
| Generic document creation (PPTs, Word docs) not grounded in company data | Commodity. Claude.ai already does this better. VEDA's value is data-grounded output. |
| Replace your CA or legal advisor | VEDA surfaces compliance information. It does not give legal advice. |
| Access data from other companies | Every query is tenant-isolated. Multi-tenant architecture makes cross-tenant access architecturally impossible. |
| Operate without human confirmation on irreversible actions | Payroll submission, invoice cancellation, employee deletion — always require explicit CONFIRM. |
| Send communications without approval | VEDA drafts and proposes. Humans approve before anything goes external. |
| Make hiring or firing decisions | VEDA can surface data. Decisions about people remain with humans. |
| Predict the future with certainty | VEDA forecasts from data trends. It flags risk, not certainty. |

---

## Indian Compliance Coverage

VEDA is the only conversational ERP interface built with Indian compliance as a first-class concern, not a plugin.

| Compliance Area | Coverage | Status |
|---|---|---|
| PF — 12% employer + 12% employee on basic | Calculation built into PayrollCalculator | ✅ Live |
| ESI — 3.25% employer + 0.75% employee | Calculation + ceiling monitoring | ✅ Live |
| Professional Tax — state-wise slab table | PT deduction by state | ✅ Live |
| TDS on salary — monthly estimated tax | TDS calculation in payroll | ✅ Live |
| GST — CGST/SGST (intra-state), IGST (inter-state) | Auto-calculation on invoices | ✅ Live |
| TDS on vendor payments — 194C, 194J | Finance module | ✅ Live |
| Invoice numbering — INV-YYYY-NNNN sequential | Finance module | ✅ Live |
| GSTIN validation on clients and company | Mandatory field enforcement | ✅ Live |
| HSN/SAC codes on line items | Mandatory field enforcement | ✅ Live |
| New Wage Code 2025 — 50% basic salary rule | Compliance check | 🔭 Future Scope |
| Income Tax Act 2025 — revised TDS/Form 16 | TDS recalculation + new form formats | 🔭 Future Scope (Phase 5) |
| Labour Code 2025 — fixed-term gratuity at 1 year | Gratuity eligibility monitoring | 🔭 Future Scope (Phase 5) |
| Digital record-keeping mandate (Labour Code 2025) | All records already digital, audit trail in DB | ✅ Architecturally covered |
| GSTR-1 and GSTR-3B filing preparation | GST return summaries | 🔭 Future Scope (Phase 5) |
| Form 24Q — quarterly TDS return | TDS return filing | 🔭 Future Scope (Phase 5) |
| Form 16 — annual employee tax certificate | PDF generation | 🔭 Future Scope (Phase 5) |

---

## Capability Count by Status

| Status | Count |
|---|---|
| ✅ Live today | ~12 |
| 📋 Planned (Phases 3–4) | ~35 |
| 🔭 Future Scope (Phase 5+) | ~45 |
| ❌ Out of scope | 7 |

---

## Why VEDA's Capabilities Are Different From Competitors

| Capability | greytHR | Keka | Zoho People | SAP Joule | **VEDA** |
|---|---|---|---|---|---|
| Natural language operations | ❌ | ❌ | ❌ | ✅ (enterprise only) | ✅ |
| Inline interactive cards in chat | ❌ | ❌ | ❌ | ❌ | ✅ |
| Human-in-the-loop approval in chat | ❌ | ❌ | ❌ | Partial | ✅ |
| Proactive alerts without being asked | Partial | Partial | Partial | Partial | ✅ (planned) |
| Indian compliance built-in, not bolted on | ✅ | ✅ | Partial | ❌ | ✅ |
| Reports grounded in live company data | ❌ | Partial | Partial | Partial | ✅ (planned) |
| WhatsApp integration for Indian SMEs | Partial | ❌ | ❌ | ❌ | ✅ (planned) |
| First seat free | ❌ | ❌ | ❌ | ❌ | ✅ |
| Designed for 1–50 employee Indian SME | ✅ | Partial | ❌ | ❌ | ✅ |

---

*Last updated: March 2026 — reflects Task 3.1 and 3.2 implementation status.*
*Update this file when each task is completed and capabilities move from Planned → Live.*