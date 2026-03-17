'use client';
import { useState } from 'react';
import { Users, DollarSign, Settings, BarChart2, Home as HomeIcon, FileText } from 'lucide-react';
import { VEDAMessageBubble } from '@/components/veda/VEDAMessage';
import { VEDAMessage, UserRole, UIAction } from '@/types/ui-response';

// ── Mock user (replace with JWT context in Task 4.2) ──────────────────────
const MOCK_USER = {
  role: 'owner' as UserRole,
  full_name: 'Arnab Roy',
  company_name: 'Udoo Demo Co.',
};

// ── RBAC: which modules each role can see ─────────────────────────────────
const MODULE_ACCESS: Record<UserRole, string[]> = {
  owner:           ['home', 'hrms', 'payroll', 'finance', 'settings'],
  hr_manager:      ['home', 'hrms', 'payroll'],
  finance_manager: ['home', 'finance'],
  manager:         ['home', 'hrms'],
  employee:        ['home', 'hrms'],
  auditor:         ['home', 'hrms', 'payroll', 'finance'],
};

const MODULE_ICONS: Record<string, React.ReactNode> = {
  home:     <HomeIcon size={18} />,
  hrms:     <Users size={18} />,
  payroll:  <BarChart2 size={18} />,
  finance:  <DollarSign size={18} />,
  settings: <Settings size={18} />,
};

// ── Mock VEDA conversation ────────────────────────────────────────────────
const MOCK_MESSAGES: VEDAMessage[] = [
  {
    id: '1',
    role: 'assistant',
    content: "Hello Arnab! I'm VEDA, your AI business assistant. What would you like to do today?",
    response: {
      type: 'text',
      message: "Hello! I'm VEDA.",
      payload: {
        content: "Hello Arnab! I'm VEDA, your AI business assistant.",
        hints: ["Show all employees", "Run payroll", "Pending approvals"],
      },
      actions: [],
      context: { open_record_type: null, open_record_id: null, open_module: null, tenant_id: 'demo' },
    },
    timestamp: new Date(),
  },
  {
    id: '2',
    role: 'user',
    content: 'Show me all active employees',
    timestamp: new Date(),
  },
  {
    id: '3',
    role: 'assistant',
    content: 'Here are the active employees (3 total):',
    response: {
      type: 'table',
      message: 'Here are the active employees (3 total):',
      payload: {
        columns: ['employee_number', 'employee_name', 'designation', 'department', 'status'],
        column_labels: {
          employee_number: 'ID',
          employee_name: 'Name',
          designation: 'Designation',
          department: 'Department',
          status: 'Status',
        },
        rows: [
          { id: 'uuid-1', employee_number: 'EMP-001', employee_name: 'Priya Sharma', designation: 'HR Manager', department: 'Human Resources', status: 'Active' },
          { id: 'uuid-2', employee_number: 'EMP-002', employee_name: 'Dev Patel', designation: 'Machine Operator', department: 'Production', status: 'Active' },
          { id: 'uuid-3', employee_number: 'EMP-003', employee_name: 'Kiran Patel', designation: 'Finance Manager', department: 'Finance', status: 'Active' },
        ],
        total: 3,
        record_type: 'employee',
        row_id_field: 'id',
      },
      actions: [
        { action_id: 'add_employee', label: 'Add Employee', style: 'primary', endpoint: '/api/employees/', method: 'POST', payload: {}, confirmation_required: false },
      ],
      context: { open_record_type: null, open_record_id: null, open_module: 'hrms', tenant_id: 'demo' },
    },
    timestamp: new Date(),
  },
  {
    id: '4',
    role: 'user',
    content: 'Approve Dev Patel\'s leave',
    timestamp: new Date(),
  },
  {
    id: '5',
    role: 'assistant',
    content: "Please confirm the approval for Dev Patel's leave request:",
    response: {
      type: 'approval',
      message: "Please confirm the approval for Dev Patel's leave request:",
      payload: {
        record_type: 'leave_application',
        record_id: 'uuid-leave-1',
        summary: {
          Employee: 'Dev Patel',
          'Leave Type': 'Casual Leave',
          From: '2026-03-18',
          To: '2026-03-20',
          Days: '3',
          Reason: 'Family function',
        },
        action_options: ['Approve', 'Reject'],
      },
      actions: [
        { action_id: 'approve', label: 'Approve', style: 'primary', endpoint: '/api/leave-applications/uuid-leave-1/approve', method: 'POST', payload: {}, confirmation_required: false },
        { action_id: 'reject', label: 'Reject', style: 'danger', endpoint: '/api/leave-applications/uuid-leave-1/cancel', method: 'POST', payload: {}, confirmation_required: false },
      ],
      context: { open_record_type: 'leave_application', open_record_id: 'uuid-leave-1', open_module: 'hrms', tenant_id: 'demo' },
    },
    timestamp: new Date(),
  },
];

export default function Home() {
  const [activeModule, setActiveModule] = useState('hrms');
  const [messages] = useState<VEDAMessage[]>(MOCK_MESSAGES);
  const [inputValue, setInputValue] = useState('');
  const visibleModules = MODULE_ACCESS[MOCK_USER.role];

  const handleAction = (action: UIAction) => {
    console.log('Action triggered:', action);
    // Task 4.2: wire to real API calls
  };

  const handleHintClick = (hint: string) => {
    setInputValue(hint);
  };

  return (
    <div className="flex flex-col h-screen bg-[var(--bg-base)] overflow-hidden">

      {/* TOP BAR */}
      <div
        className="flex items-center justify-between px-4 border-b border-[var(--border-subtle)] flex-shrink-0"
        style={{ height: 'var(--top-bar-height)' }}
      >
        <div className="flex items-center gap-3">
          <span className="text-[var(--veda-purple)] font-bold tracking-widest text-sm">UDOO</span>
          <span className="text-[var(--border-default)]">|</span>
          <span className="text-[var(--text-secondary)] text-xs">{MOCK_USER.company_name}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[var(--text-muted)] text-xs">{MOCK_USER.full_name}</span>
          <div className="px-2 py-0.5 rounded bg-[var(--veda-purple-bg)] text-[var(--veda-purple)] text-xs border border-[var(--accent-primary)]">
            {MOCK_USER.role}
          </div>
        </div>
      </div>

      {/* MAIN AREA */}
      <div className="flex flex-1 overflow-hidden">

        {/* ACTIVITY BAR */}
        <div
          className="flex flex-col items-center py-2 gap-1 border-r border-[var(--border-subtle)] bg-[var(--bg-panel)] flex-shrink-0"
          style={{ width: 'var(--activity-bar-width)' }}
        >
          {visibleModules.map(mod => (
            <button
              key={mod}
              onClick={() => setActiveModule(mod)}
              title={mod.toUpperCase()}
              className={`
                w-9 h-9 flex items-center justify-center rounded transition-colors
                ${activeModule === mod
                  ? 'text-[var(--text-primary)] bg-[var(--bg-panel-hover)]'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'}
              `}
            >
              {MODULE_ICONS[mod]}
            </button>
          ))}
        </div>

        {/* LEFT PANEL */}
        <div
          className="flex flex-col border-r border-[var(--border-subtle)] bg-[var(--bg-panel)] flex-shrink-0 overflow-hidden"
          style={{ width: 'var(--left-panel-width)' }}
        >
          <div className="px-3 py-2 border-b border-[var(--border-subtle)]">
            <span className="text-[var(--text-muted)] text-xs uppercase tracking-wider">
              {activeModule.toUpperCase()}
            </span>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            <p className="text-[var(--text-muted)] text-xs px-2 py-1">
              Record navigator — Task 4.3
            </p>
          </div>
        </div>

        {/* CENTER PANEL — VEDA CONVERSATION */}
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            {messages.map(msg => (
              <VEDAMessageBubble
                key={msg.id}
                msg={msg}
                onAction={handleAction}
                onHintClick={handleHintClick}
              />
            ))}
          </div>

          {/* Input */}
          <div className="flex-shrink-0 border-t border-[var(--border-subtle)] p-3">
            <div className="flex gap-2 items-center bg-[var(--bg-input)] border border-[var(--border-default)] rounded px-3 py-2 focus-within:border-[var(--border-active)]">
              <span className="text-[var(--veda-purple)] text-xs font-bold flex-shrink-0">VEDA</span>
              <span className="text-[var(--border-default)]">›</span>
              <input
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                placeholder="Ask VEDA anything..."
                className="flex-1 bg-transparent text-[var(--text-primary)] text-xs outline-none placeholder:text-[var(--text-muted)]"
              />
              <kbd className="text-[var(--text-muted)] text-xs">⏎</kbd>
            </div>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div
          className="flex flex-col border-l border-[var(--border-subtle)] bg-[var(--bg-panel)] flex-shrink-0 overflow-hidden"
          style={{ width: 'var(--right-panel-width)' }}
        >
          <div className="px-3 py-2 border-b border-[var(--border-subtle)]">
            <span className="text-[var(--text-muted)] text-xs uppercase tracking-wider">Inspector</span>
          </div>
          <div className="flex-1 overflow-y-auto p-3">
            <p className="text-[var(--text-muted)] text-xs">
              Record inspector — Task 4.3
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
