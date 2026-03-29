# Task 4.7a — Design System Migration

## CONTEXT

Read these files before doing anything else, in this exact order:
1. ARCHITECTURE.md
2. frontend/package.json
3. frontend/app/globals.css
4. frontend/components/ui/ — list all files present (ls only, don't read them)
5. frontend/tailwind.config.ts or tailwind.config.js (whichever exists)
6. frontend/components.json (if it exists)

Report what you find in each file before proceeding.
Specifically report:
- Which version of Next.js is installed
- Whether shadcn/ui is already initialised (components.json exists?)
- Which shadcn components are already installed (list from frontend/components/ui/)
- Which version of Tailwind CSS is installed (v3 or v4?)
- Whether @tanstack/react-table is already installed
- Whether framer-motion is installed (should NOT be — do not install it)

---

## TASK

Establish the complete design system foundation for Udoo's Classic and
VEDA Assist modes. This is a one-time migration. Every subsequent frontend
task (4.0, 4.7, 4.8, 4.9+) builds on top of this foundation.

This task has FOUR parts. Execute them in order.

---

## PART 1 — Initialise shadcn/ui (if not already done)

Check if `frontend/components.json` exists.

If it does NOT exist, run:
```bash
cd frontend
npx shadcn@latest init
```

When prompted, answer:
- Style: New York
- Base color: Blue
- CSS variables: Yes

If components.json ALREADY exists, skip to Part 2.
Do not re-initialise if already done.

---

## PART 2 — Install required shadcn blocks and components

Run each command from inside the `frontend/` directory.

### Core components (used everywhere):
```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add form
npx shadcn@latest add select
npx shadcn@latest add textarea
npx shadcn@latest add checkbox
npx shadcn@latest add radio-group
npx shadcn@latest add switch
npx shadcn@latest add badge
npx shadcn@latest add card
npx shadcn@latest add separator
npx shadcn@latest add dialog
npx shadcn@latest add sheet
npx shadcn@latest add dropdown-menu
npx shadcn@latest add popover
npx shadcn@latest add tooltip
npx shadcn@latest add toast
npx shadcn@latest add alert
npx shadcn@latest add avatar
npx shadcn@latest add tabs
npx shadcn@latest add table
npx shadcn@latest add skeleton
npx shadcn@latest add scroll-area
npx shadcn@latest add calendar
npx shadcn@latest add date-picker
npx shadcn@latest add breadcrumb
npx shadcn@latest add progress
```

### Sidebar component (foundation for Classic + VEDA Assist shells):
```bash
npx shadcn@latest add sidebar
```

### Blocks (full pre-built layouts):
```bash
npx shadcn@latest add sidebar-07
npx shadcn@latest add sidebar-15
npx shadcn@latest add dashboard-01
npx shadcn@latest add login-04
```

### TanStack Table (for all list/data pages):
```bash
npm install @tanstack/react-table
```

After all installs, run:
```bash
ls frontend/components/ui/ | wc -l
```
Expected: at least 25 component files.

---

## PART 3 — Update globals.css with Udoo design tokens

This step establishes the visual identity for Classic and VEDA Assist modes.
VEDA Auto (the existing dark IDE shell) is NOT touched.

Replace the `:root` and `.dark` sections in `frontend/app/globals.css`
with the following. Preserve any existing custom CSS below the token section
(VEDA Auto shell styles, card styles, etc.) — only replace the CSS variables block.

The new token block to use:

```css
@layer base {
  :root {
    /* Udoo brand — light theme (Classic + VEDA Assist) */
    --background: 0 0% 100%;
    --foreground: 224 71.4% 4.1%;

    --card: 0 0% 100%;
    --card-foreground: 224 71.4% 4.1%;

    --popover: 0 0% 100%;
    --popover-foreground: 224 71.4% 4.1%;

    /* Udoo primary — Blue 600 (shadcn blue base) */
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;

    /* Secondary — Slate 100 */
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    /* Muted — Slate 50 */
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    /* Accent — Blue 50 */
    --accent: 214.3 31.8% 91.4%;
    --accent-foreground: 222.2 47.4% 11.2%;

    /* Destructive — Red 600 */
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;

    --radius: 0.5rem;

    /* VEDA diff attribution — purple tint for VEDA-filled fields */
    /* Intentionally distinct from brand blue — do not change */
    --veda-fill: 258 100% 96%;
    --veda-fill-border: 258 90% 66%;

    /* Status colours — used in badges across all modes */
    --status-active: 142 71% 45%;
    --status-inactive: 215.4 16.3% 46.9%;
    --status-pending: 38 92% 50%;
    --status-approved: 142 71% 45%;
    --status-rejected: 0 84.2% 60.2%;
    --status-draft: 215.4 16.3% 46.9%;
    --status-submitted: 221.2 83.2% 53.3%;

    /* Sidebar tokens */
    --sidebar-background: 0 0% 98%;
    --sidebar-foreground: 222.2 47.4% 11.2%;
    --sidebar-primary: 221.2 83.2% 53.3%;
    --sidebar-primary-foreground: 210 40% 98%;
    --sidebar-accent: 214.3 31.8% 91.4%;
    --sidebar-accent-foreground: 222.2 47.4% 11.2%;
    --sidebar-border: 214.3 31.8% 91.4%;
    --sidebar-ring: 221.2 83.2% 53.3%;
  }

  .dark {
    /* VEDA Auto dark IDE shell — keep existing dark theme */
    --background: 224 71.4% 4.1%;
    --foreground: 210 20% 98%;

    --card: 224 71.4% 4.1%;
    --card-foreground: 210 20% 98%;

    --popover: 224 71.4% 4.1%;
    --popover-foreground: 210 20% 98%;

    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;

    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;

    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;

    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;

    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 20% 98%;

    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 221.2 83.2% 53.3%;

    --veda-fill: 258 40% 18%;
    --veda-fill-border: 258 90% 66%;

    --sidebar-background: 240 5.9% 10%;
    --sidebar-foreground: 210 40% 98%;
    --sidebar-primary: 221.2 83.2% 53.3%;
    --sidebar-primary-foreground: 210 40% 98%;
    --sidebar-accent: 217.2 32.6% 17.5%;
    --sidebar-accent-foreground: 210 40% 98%;
    --sidebar-border: 217.2 32.6% 17.5%;
    --sidebar-ring: 221.2 83.2% 53.3%;
  }
}
```

After writing, verify the file contains `--veda-fill` by running:
```bash
grep "veda-fill" frontend/app/globals.css
```
Expected: 4 lines containing `--veda-fill`.

---

## PART 4 — Create design system reference file

Create `frontend/lib/design-system.ts` with the following content.
This file is the single source of truth for all colour names, badge variants,
and status mappings used across all pages.

```typescript
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

export type VEDAMode = "veda-auto" | "veda-assist" | "classic"

export const VEDA_MODE_LABELS: Record<VEDAMode, string> = {
  "veda-auto":   "VEDA Auto",
  "veda-assist": "VEDA Assist",
  "classic":     "Classic",
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
```

After creating, verify with:
```bash
cat frontend/lib/design-system.ts | head -5
```
Expected: first line is the JSDoc comment block.

---

## VERIFICATION

Run all four checks and show raw output:

```bash
# 1. shadcn initialised
cat frontend/components.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('style:', d.get('style'), '| baseColor:', d.get('tailwind',{}).get('baseColor'))"

# 2. Key components installed
ls frontend/components/ui/ | grep -E "sidebar|table|form|button|card|badge|select|dialog|tabs" | sort

# 3. TanStack Table installed
cat frontend/package.json | python3 -c "import sys,json; d=json.load(sys.stdin); deps={**d.get('dependencies',{}),**d.get('devDependencies',{})}; print('tanstack:', deps.get('@tanstack/react-table','NOT FOUND'))"

# 4. Design tokens present
grep -c "veda-fill\|--primary\|--sidebar-primary" frontend/app/globals.css

# 5. Design system file exists
wc -l frontend/lib/design-system.ts
```

Expected results:
1. style: new-york | baseColor: blue
2. At least 8 matching files listed
3. tanstack: version number (not NOT FOUND)
4. At least 8 matches
5. At least 100 lines

---

## COMMIT

```bash
cd frontend && git add -A
git status
git commit -m "feat: Task 4.7a — design system migration, shadcn full install, Udoo tokens"
```

Show full git output. DO NOT push.

---

## IMPORTANT NOTES

1. Do NOT modify `frontend/app/page.tsx` — the VEDA Auto shell stays untouched
2. Do NOT install framer-motion — it is not needed
3. Do NOT install Magic UI — it is not needed
4. If any shadcn add command asks "would you like to overwrite?" — answer YES
5. If components.json already shows New York style, skip Part 1 entirely
6. The sidebar-07, sidebar-15, dashboard-01, login-04 blocks create files
   in frontend/components/ — do not delete them, they are the starting
   point for Tasks 4.7, 4.8, 4.9, 4.10 etc.
