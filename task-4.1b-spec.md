# Task 4.1b — Shell Redesign (VEDA Right Panel)

## Why this task exists

The previous "4-panel IDE" layout (Left: Recent, Center: VEDA, Right: Context, Bottom: Logs) was built for initial AI-engine debugging. It was optimized for watching the AI work, not for a human to manage an ERP.

**The shift:**
Udoo is moving to an **ERP-First Shell**. The center stage belongs to the business data (Employees, Leaves, Invoices). VEDA moves to the Right Panel, acting as a co-pilot that can be toggled between **Auto** (Agentic) and **Assist** (Chat-only) modes.

---

## Layout Specification

```
┌──────┬──────────────┬──────────────────────────────────────┬───────────────────┐
│      │              │  Employees │ Dev Patel │ INV-004 │ + │  VEDA  [Auto ▾]   │
│  A   │   EXPLORER   ├────────────┴──────────┴─────────┴────┤                   │
│  C   │   (module    │                                      │  Chat messages    │
│  T   │    tree)     │      ERP CONTENT                     │  Cards inline     │
│  I   │              │                                      │  Action results   │
│  V   │              │  Default: Welcome / onboarding       │                   │
│  I   │              │  Or: DataTable list page              │                   │
│  T   │              │  Or: Record detail form               │                   │
│  Y   │              │                                      │  [Ask VEDA...]    │
└──────┴──────────────┴──────────────────────────────────────┴───────────────────┘
 48px    260px                    flex: 1                        340px
```

### 1. Activity Bar (48px)
- Fixed vertical strip on the far left.
- Icons: Home, HRMS, Payroll, Finance, Settings.
- Provides high-level module switching.

### 2. Explorer Panel (resizable, 180px - 400px)
- Localized navigation for the active module.
- Hierarchical tree (e.g., HRMS > Employees, HRMS > Leave Applications).
- Badges for record counts (e.g., "5 Pending Leaves").

### 3. Center ERP Surface (flex: 1)
- **Tab Bar**: Manages open ERP records/lists. VEDA is NOT a tab.
- **Content**:
  - **Welcome Screen**: Shown when no tabs are open. Contains quick actions and stats.
  - **List Pages**: Searchable/filterable tables of records.
  - **Detail Pages**: Full forms for individual records (e.g., Employee profile).

### 4. VEDA Right Panel (resizable, 280px - 500px)
- The persistent home for the AI agent.
- **Mode Toggle**: Dropdown in the header (Auto, Assist).
- **Chat Interface**: The conversation window.
- **Context Awareness**: VEDA automatically tracks which ERP tab is currently focused.

---

## Interactive Features

### Resizability
- Drag handles between Activity-Explorer, Explorer-Center, and Center-VEDA.
- Panel widths persist in `localStorage`.

### Toggles
- Explorer can be collapsed via Activity bar icons or a chevron.
- VEDA panel can be collapsed to enter "Classic Mode".

### Tab Management
- Dynamic opening: Clicking an item in Explorer opens a new tab.
- State: Tabs track "dirty" state (unsaved changes).
- Tab persistence: Open tabs survive page refreshes.

---

## Implementation Rules

1. **Vanilla CSS for Layout**: Use Flexbox and Grid. No heavy layout libraries.
2. **Context Passing**: When a tab is switched in the Center, a message must be sent to the VEDA component to update its `active_record_id` and `active_record_type`.
3. **Mode Switching**: Moving from "Auto" to "Assist" only changes the UI rendering of action buttons in the chat (Auto shows them, Assist hides/disables them). No backend change required.
