'use client';
import { useState, useRef, useEffect } from 'react';
import { Users, DollarSign, Settings, BarChart2, Home as HomeIcon, Send } from 'lucide-react';
import { VEDAMessageBubble } from '@/components/veda/VEDAMessage';
import { VEDAMessage, UserRole, UIAction, UIContext } from '@/types/ui-response';
import { sendVEDAMessage, buildNullContext, executeAction } from '@/lib/veda-client';
import { ThemeToggle } from '@/components/theme-toggle';

// ── Mock user (replace with JWT context in Task 4.3) ──────────────────────
const MOCK_USER = {
  role: 'owner' as UserRole,
  full_name: 'Arnab Roy',
  company_name: 'Udoo Demo Co.',
};

// ── RBAC: which modules each role can see ─────────────────────────────────
const MODULE_ACCESS: Record<UserRole, string[]> = {
  owner: ['home', 'hrms', 'payroll', 'finance', 'settings'],
  hr_manager: ['home', 'hrms', 'payroll'],
  finance_manager: ['home', 'finance'],
  manager: ['home', 'hrms'],
  employee: ['home', 'hrms'],
  auditor: ['home', 'hrms', 'payroll', 'finance'],
};

const ROLE_HINTS: Record<UserRole, string[]> = {
  owner: ["Show all employees", "Run payroll", "Pending approvals"],
  hr_manager: ["Approve leaves", "Run payroll", "View attendance"],
  finance_manager: ["Outstanding invoices", "Create quote", "Payment received"],
  manager: ["Approve team leaves", "View team attendance", "My team"],
  employee: ["Apply for leave", "My payslips", "My attendance"],
  auditor: ["Show all employees", "View payroll", "Show invoices"],
};

const MODULE_ICONS: Record<string, React.ReactNode> = {
  home: <HomeIcon size={18} />,
  hrms: <Users size={18} />,
  payroll: <BarChart2 size={18} />,
  finance: <DollarSign size={18} />,
  settings: <Settings size={18} />,
};

let messageIdCounter = 0;
function nextId() { return String(++messageIdCounter); }

export default function Home() {
  const [activeModule, setActiveModule] = useState('hrms');
  const [messages, setMessages] = useState<VEDAMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeContext, setActiveContext] = useState<UIContext>(buildNullContext());
  const [recentRecords, setRecentRecords] = useState<
    { type: string; id: string; label: string; module: string }[]
  >([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const visibleModules = MODULE_ACCESS[MOCK_USER.role];

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Build conversation history from current messages (last 10)
  function buildHistory() {
    return messages
      .slice(-10)
      .map(m => ({
        role: m.role === 'assistant' ? 'assistant' : 'user',
        content: m.content,
      }));
  }

  async function handleSend() {
    const text = inputValue.trim();
    if (!text || isLoading) return;

    setInputValue('');

    // Add user message immediately
    const userMsg: VEDAMessage = {
      id: nextId(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const vedaResponse = await sendVEDAMessage({
        message: text,
        context: activeContext,
        conversation_history: buildHistory(),
      });

      // Update active context from response
      if (vedaResponse.context) {
        setActiveContext(vedaResponse.context);
      }

      const assistantMsg: VEDAMessage = {
        id: nextId(),
        role: 'assistant',
        content: vedaResponse.message,
        response: vedaResponse,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);

    } catch (err) {
      // Show error as a BLOCKER card
      const errorMsg: VEDAMessage = {
        id: nextId(),
        role: 'assistant',
        content: 'I encountered an error processing your request.',
        response: {
          type: 'blocker',
          message: 'I encountered an error processing your request.',
          payload: {
            reason: err instanceof Error ? err.message : 'Unknown error. Is the backend running?',
            resolution_options: [],
            blocked_task: text,
          },
          actions: [],
          context: activeContext,
        },
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleHintClick(hint: string) {
    setInputValue(hint);
  }

  async function handleAction(action: UIAction) {
    // Skip actions with no endpoint (e.g. dismiss/cancel)
    if (!action.endpoint) return;

    try {
      const result = await executeAction(
        action.endpoint,
        action.method,
        action.payload,
      );

      if (result.ok) {
        // Action succeeded — send follow-up to VEDA
        const followUpText = `Action completed: ${action.label}`;
        const userMsg: VEDAMessage = {
          id: nextId(),
          role: 'user',
          content: followUpText,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMsg]);
        setIsLoading(true);

        try {
          const vedaResponse = await sendVEDAMessage({
            message: followUpText,
            context: activeContext,
            conversation_history: buildHistory(),
          });

          if (vedaResponse.context) {
            setActiveContext(vedaResponse.context);
          }

          const assistantMsg: VEDAMessage = {
            id: nextId(),
            role: 'assistant',
            content: vedaResponse.message,
            response: vedaResponse,
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, assistantMsg]);
        } finally {
          setIsLoading(false);
        }

      } else {
        // Action failed — show error in chat
        const errorMsg: VEDAMessage = {
          id: nextId(),
          role: 'assistant',
          content: `Action failed: ${action.label}`,
          response: {
            type: 'blocker',
            message: `Action failed: ${action.label}`,
            payload: {
              reason: `The ${action.label} action failed with status ${result.status}. Please try again.`,
              resolution_options: [],
              blocked_task: action.label,
            },
            actions: [],
            context: activeContext,
          },
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMsg]);
      }

    } catch (err) {
      const errorMsg: VEDAMessage = {
        id: nextId(),
        role: 'assistant',
        content: 'Action failed due to a network error.',
        response: {
          type: 'blocker',
          message: 'Action failed due to a network error.',
          payload: {
            reason: err instanceof Error ? err.message : 'Network error',
            resolution_options: [],
            blocked_task: action.label,
          },
          actions: [],
          context: activeContext,
        },
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMsg]);
    }
  }

  function handleRowClick(recordType: string, recordId: string) {
    const newContext = {
      ...activeContext,
      open_record_type: recordType,
      open_record_id: recordId,
    };
    setActiveContext(newContext);

    // Track in recent records (keep last 5, no duplicates)
    setRecentRecords(prev => {
      const label = `${recordType} ${recordId.slice(0, 6)}...`;
      const entry = { type: recordType, id: recordId, label, module: activeModule };
      const filtered = prev.filter(r => r.id !== recordId);
      return [entry, ...filtered].slice(0, 5);
    });
  }

  return (
    <div className="flex flex-col h-screen bg-(--bg-base) overflow-hidden transition-colors duration-300 font-sans">

      {/* TOP BAR */}
      <div
        className="flex items-center justify-between px-4 border-b border-(--border-subtle) flex-shrink-0 bg-(--bg-panel)/80 backdrop-blur-md z-30"
        style={{ height: 'var(--top-bar-height)' }}
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-gradient-to-tr from-(--veda-purple) to-[#a855f7] flex items-center justify-center shadow-(--veda-glow)">
              <span className="text-white font-bold text-xs">U</span>
            </div>
            <span className="text-(--text-primary) font-bold tracking-tight text-sm">UDOO</span>
          </div>
          <span className="text-(--border-default) font-light">|</span>
          <span className="text-(--text-secondary) text-xs font-medium">{MOCK_USER.company_name}</span>
        </div>
        <div className="flex items-center gap-4">
          {activeContext.open_record_type && (
            <div className="hidden md:flex items-center gap-2 px-2 py-1 rounded-full bg-(--bg-panel-hover) border border-(--border-subtle)">
              <div className="w-1.5 h-1.5 rounded-full bg-(--veda-purple) animate-pulse" />
              <span className="text-(--text-muted) text-[10px] uppercase tracking-wider font-bold">
                {activeContext.open_record_type}
              </span>
            </div>
          )}
          <div className="flex items-center gap-3">
            <span className="text-(--text-secondary) text-xs">{MOCK_USER.full_name}</span>
            <div className="px-2 py-0.5 rounded-md bg-(--veda-purple-bg) text-(--veda-purple) text-[10px] font-bold border border-(--veda-purple-border) uppercase">
              {MOCK_USER.role}
            </div>
          </div>
          <div className="h-4 w-px bg-(--border-subtle)" />
          <ThemeToggle />
        </div>
      </div>

      {/* MAIN AREA */}
      <div className="flex flex-1 overflow-hidden">

        {/* ACTIVITY BAR */}
        <div
          className="flex flex-col items-center py-4 gap-2 border-r border-(--border-subtle) bg-(--bg-panel) flex-shrink-0 z-20"
          style={{ width: 'var(--activity-bar-width)' }}
        >
          {visibleModules.map(mod => (
            <button
              key={mod}
              onClick={() => {
                setActiveModule(mod);
                setActiveContext(prev => ({ ...prev, open_module: mod }));
              }}
              title={mod.toUpperCase()}
              className={`
                w-10 h-10 flex items-center justify-center rounded-xl transition-all duration-200
                ${activeModule === mod
                  ? 'text-(--veda-purple) bg-(--veda-purple-bg) shadow-sm'
                  : 'text-(--text-muted) hover:text-(--text-primary) hover:bg-(--bg-panel-hover)'}
              `}
            >
              {MODULE_ICONS[mod]}
            </button>
          ))}
          <div className="mt-auto pb-2 text-(--text-muted)">
            <Settings size={18} className="cursor-pointer hover:text-(--text-primary) transition-colors" />
          </div>
        </div>

        {/* LEFT PANEL */}
        <div
          className="flex flex-col border-r border-(--border-subtle) bg-(--bg-panel)/50 flex-shrink-0 overflow-hidden"
          style={{ width: 'var(--left-panel-width)' }}
        >
          <div className="px-4 py-3 border-b border-(--border-subtle) flex items-center justify-between">
            <span className="text-(--text-primary) text-[11px] font-bold uppercase tracking-widest">
              {activeModule}
            </span>
          </div>
          <div className="flex-1 overflow-y-auto">
            {recentRecords.length === 0 ? (
              <div className="px-4 py-8 text-center">
                <p className="text-(--text-muted) text-xs italic">
                    No records opened.
                </p>
              </div>
            ) : (
              <div className="py-2">
                <p className="text-(--text-muted) text-[10px] px-4 py-2 uppercase tracking-widest font-bold opacity-60">
                  Recent Records
                </p>
                {recentRecords.map(rec => (
                  <button
                    key={rec.id}
                    onClick={() => setActiveContext(prev => ({
                      ...prev,
                      open_record_type: rec.type,
                      open_record_id: rec.id,
                      open_module: rec.module,
                    }))}
                    className={`
                      w-full text-left px-4 py-2 text-xs transition-all
                      hover:bg-(--bg-panel-hover) group
                      ${activeContext.open_record_id === rec.id
                        ? 'text-(--text-primary) bg-(--bg-panel-hover) border-r-2 border-(--veda-purple)'
                        : 'text-(--text-secondary)'}
                    `}
                  >
                    <div className="flex flex-col">
                      <span className="text-(--veda-purple) text-[10px] font-bold uppercase tracking-tighter group-hover:opacity-100 opacity-70">
                        {rec.type}
                      </span>
                      <span className="truncate">{rec.id.slice(0, 12)}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* CENTER PANEL — VEDA CONVERSATION */}
        <div className="flex flex-col flex-1 overflow-hidden bg-gradient-to-b from-(--bg-base) to-(--bg-panel)/20 relative">

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
            {messages.length === 0 && !isLoading && (
              <div className="flex flex-col items-center justify-center h-full gap-5 max-w-2xl mx-auto text-center animate-in fade-in zoom-in duration-500">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-(--veda-purple) to-[#a855f7] flex items-center justify-center shadow-xl shadow-(--veda-glow) transform hover:scale-105 transition-transform duration-300">
                  <span className="text-white font-bold text-3xl">V</span>
                </div>
                <div className="space-y-2">
                  <h2 className="text-(--text-primary) text-xl font-bold tracking-tight">Welcome, {MOCK_USER.full_name}</h2>
                  <p className="text-(--text-secondary) text-sm px-4">
                    I am VEDA, your AI-Native ERP orchestration engine. Ask me to run payroll, approve leaves, or generate financial insights.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center mt-4">
                  {ROLE_HINTS[MOCK_USER.role].map(hint => (
                    <button
                      key={hint}
                      onClick={() => handleHintClick(hint)}
                      className="px-4 py-2 rounded-xl bg-(--bg-panel) border border-(--border-subtle) text-(--text-secondary) text-xs hover:border-(--veda-purple-border) hover:text-(--veda-purple) hover:bg-(--veda-purple-bg) transition-all shadow-sm"
                    >
                      {hint}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map(msg => (
                <VEDAMessageBubble
                  key={msg.id}
                  msg={msg}
                  onAction={handleAction}
                  onRowClick={handleRowClick}
                  onHintClick={handleHintClick}
                />
              ))}

              {/* Typing indicator */}
              {isLoading && (
                <div className="flex items-start gap-4 mb-4 animate-in fade-in duration-300">
                  <div className="w-8 h-8 rounded-lg bg-(--veda-purple) flex items-center justify-center shadow-lg shadow-(--veda-glow) flex-shrink-0">
                    <span className="text-white text-[10px] font-bold uppercase tracking-tighter">VEDA</span>
                  </div>
                  <div className="bg-(--bg-panel) border border-(--border-subtle) rounded-2xl px-4 py-3 flex gap-1 items-center shadow-sm">
                    <span className="w-1.5 h-1.5 rounded-full bg-(--veda-purple) animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-(--veda-purple) animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-(--veda-purple) animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              )}
            </div>

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="flex-shrink-0 p-4 bg-transparent z-10">
            <div className="max-w-3xl mx-auto relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-(--veda-purple) to-blue-500 rounded-2xl blur opacity-0 group-focus-within:opacity-20 transition-opacity duration-500" />
              <div className="relative flex min-h-[50px] gap-2 items-center bg-(--bg-panel)/90 backdrop-blur-xl border border-(--border-subtle) rounded-2xl px-4 py-2 shadow-xl focus-within:border-(--veda-purple-border) transition-all duration-300">
                <div className="w-6 h-6 rounded-md bg-(--veda-purple) flex items-center justify-center flex-shrink-0 shadow-md">
                   <span className="text-white text-[10px] font-bold uppercase tracking-tighter">V</span>
                </div>
                <input
                  type="text"
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={isLoading ? 'VEDA is thinking...' : 'Ask your ERP anything...'}
                  disabled={isLoading}
                  className="flex-1 bg-transparent text-(--text-primary) text-sm outline-none placeholder:text-(--text-muted) disabled:opacity-50"
                  id="veda-input"
                />
                <button
                  onClick={handleSend}
                  disabled={isLoading || !inputValue.trim()}
                  className="w-10 h-10 flex items-center justify-center rounded-xl bg-(--veda-purple) text-white hover:bg-violet-500 hover:scale-105 disabled:bg-(--border-subtle) disabled:text-(--text-muted) disabled:scale-100 disabled:opacity-50 transition-all shadow-lg shadow-(--veda-glow)"
                >
                   {isLoading ? (
                     <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                   ) : (
                     <Send size={18} />
                   )}
                </button>
              </div>
            </div>
          </div>

        </div>

        {/* RIGHT PANEL */}
        <div
          className="flex flex-col border-l border-(--border-subtle) bg-(--bg-panel) flex-shrink-0 overflow-hidden"
          style={{ width: 'var(--right-panel-width)' }}
        >
          <div className="px-4 py-3 border-b border-(--border-subtle)">
            <span className="text-(--text-primary) text-[11px] font-bold uppercase tracking-widest">Inspector</span>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {activeContext.open_record_type ? (
              <div className="space-y-4 animate-in fade-in slide-in-from-right-2 duration-300">
                <div className="space-y-1">
                  <p className="text-(--text-muted) text-[10px] font-bold uppercase tracking-widest opacity-60">
                    Record Info
                  </p>
                  <div className="p-3 rounded-xl bg-(--bg-panel-hover) border border-(--border-subtle) space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-(--text-secondary) text-xs">Module</span>
                      <span className="text-(--text-primary) text-xs font-bold capitalize">{activeContext.open_module}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-(--text-secondary) text-xs">Type</span>
                      <span className="text-(--veda-purple) text-xs font-bold uppercase tracking-tighter">{activeContext.open_record_type}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-(--text-secondary) text-xs">ID</span>
                      <span className="text-(--text-primary) text-xs font-mono">{activeContext.open_record_id?.slice(0, 12)}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                   <p className="text-(--text-muted) text-[10px] font-bold uppercase tracking-widest opacity-60">
                    Health Status
                  </p>
                  <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-[10px] p-2 rounded-lg flex items-center gap-2 font-bold">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    REAL-TIME SYNC ACTIVE
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center p-4">
                <div className="w-12 h-12 rounded-full border border-dashed border-(--border-default) flex items-center justify-center mb-4 opacity-50">
                  <BarChart2 className="text-(--text-muted)" size={20} />
                </div>
                <p className="text-(--text-muted) text-xs italic">
                  Select a record to inspect system metadata.
                </p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
