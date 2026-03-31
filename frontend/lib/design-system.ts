/**
 * Udoo Design System — Token Reference
 *
 * All three modes (VEDA Auto, VEDA Assist, Classic) use these
 * shared constants. Do not hardcode colour values anywhere else.
 * Always reference these exports.
 */

// ─── Badge variant mapping ─────────────────────────────────────────────────
// Maps domain status values to shadcn Badge variants + custom classes

export const LEAVE_STATUS_BADGE: Record<string, string> = {
  Draft:    "bg-muted text-muted-foreground",
  Pending:  "bg-yellow-100 text-yellow-800",
  Approved: "bg-green-100 text-green-800",
  Rejected: "bg-red-100 text-red-800",
  Cancelled:"bg-muted text-muted-foreground",
}

export const PAYROLL_STATUS_BADGE: Record<string, string> = {
  Draft:     "bg-muted text-muted-foreground",
  Submitted: "bg-blue-100 text-blue-800",
  Cancelled: "bg-red-100 text-red-800",
}

export const EMPLOYEE_STATUS_BADGE: Record<string, string> = {
  Active:   "bg-green-100 text-green-800",
  Inactive: "bg-muted text-muted-foreground",
}

export const ATTENDANCE_STATUS_BADGE: Record<string, string> = {
  Present:  "bg-green-100 text-green-800",
  Absent:   "bg-red-100 text-red-800",
  Leave:    "bg-blue-100 text-blue-800",
  "Half Day": "bg-yellow-100 text-yellow-800",
  Holiday:  "bg-purple-100 text-purple-800",
  "Week Off": "bg-muted text-muted-foreground",
}

export const INVOICE_STATUS_BADGE: Record<string, string> = {
  Draft:          "bg-muted text-muted-foreground",
  Sent:           "bg-blue-100 text-blue-800",
  "Partially Paid": "bg-yellow-100 text-yellow-800",
  Paid:           "bg-green-100 text-green-800",
  Cancelled:      "bg-red-100 text-red-800",
}

// ─── VEDA mode identifiers ─────────────────────────────────────────────────
// Canonical type lives in @/types/shell.ts — re-export for convenience

import type { VEDAMode } from "@/types/shell"
export type { VEDAMode }

export const VEDA_MODE_LABELS: Record<VEDAMode, string> = {
  "auto":   "VEDA Auto",
  "assist": "VEDA Assist",
}

// ─── Module navigation config ──────────────────────────────────────────────
// Used by Classic and VEDA Assist sidebar to build navigation.
// RBAC filtering is applied at render time — do not filter here.

import {
  Users, Calendar, Clock, DollarSign,
  FileText, Building2, Settings, Shield,
} from "lucide-react"

export const NAV_MODULES = [
  {
    id: "hrms",
    label: "HRMS",
    icon: Users,
    requiredModule: "hrms",
    items: [
      { label: "Employees", href: "/hrms/employees" },
      { label: "Leave", href: "/hrms/leave" },
      { label: "Attendance", href: "/hrms/attendance" },
    ],
  },
  {
    id: "payroll",
    label: "Payroll",
    icon: DollarSign,
    requiredModule: "payroll",
    items: [
      { label: "Salary Structures", href: "/payroll/structures" },
      { label: "Salary Slips", href: "/payroll/slips" },
    ],
  },
  {
    id: "finance",
    label: "Finance",
    icon: FileText,
    requiredModule: "finance",
    items: [
      { label: "Clients", href: "/finance/clients" },
      { label: "Quotes", href: "/finance/quotes" },
      { label: "Invoices", href: "/finance/invoices" },
      { label: "Payments", href: "/finance/payments" },
    ],
  },
  {
    id: "setup",
    label: "Setup",
    icon: Settings,
    requiredModule: "settings",
    items: [
      { label: "Company", href: "/setup/company" },
      { label: "Departments", href: "/setup/departments" },
      { label: "Designations", href: "/setup/designations" },
      { label: "Employment Types", href: "/setup/employment-types" },
      { label: "Branches", href: "/setup/branches" },
      { label: "Leave Types", href: "/setup/leave-types" },
      { label: "Salary Components", href: "/setup/salary-components" },
      { label: "Salary Structures", href: "/setup/salary-structures" },
      { label: "Holiday List", href: "/setup/holidays" },
    ],
  },
  {
    id: "admin",
    label: "Admin",
    icon: Shield,
    requiredModule: "settings",
    ownerOnly: true,
    items: [
      { label: "Users", href: "/admin/users" },
    ],
  },
]

// ─── Currency formatting ────────────────────────────────────────────────────

export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

// ─── Date formatting ───────────────────────────────────────────────────────

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  })
}
