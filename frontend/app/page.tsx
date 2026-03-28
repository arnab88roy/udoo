'use client';
import { useState, useRef, useEffect } from 'react';
import { Users, DollarSign, Settings, BarChart2, Home as HomeIcon, Send } from 'lucide-react';
import { VEDAMessageBubble } from '@/components/veda/VEDAMessage';
import { VEDAMessage, UserRole, UIAction, UIContext } from '@/types/ui-response';
import { sendVEDAMessage, buildNullContext, executeAction } from '@/lib/veda-client';

// ── Mock user (replace with JWT context in Task 4.3) ──────────────────────
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
          {activeContext.open_record_type && (
            <span className="text-[var(--text-muted)] text-xs">
              {activeContext.open_record_type} open
            </span>
          )}
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
              onClick={() => {
                setActiveModule(mod);
                setActiveContext(prev => ({ ...prev, open_module: mod }));
              }}
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
          <div className="flex-1 overflow-y-auto">
            {recentRecords.length === 0 ? (
              <p className="text-[var(--text-muted)] text-xs px-3 py-2">
                No records opened yet.
              </p>
            ) : (
              <div>
                <p className="text-[var(--text-muted)] text-xs px-3 py-2 uppercase tracking-wider">
                  Recent
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
                      w-full text-left px-3 py-1.5 text-xs transition-colors
                      hover:bg-[var(--bg-panel-hover)]
                      ${activeContext.open_record_id === rec.id
                        ? 'text-[var(--text-primary)] border-l-2 border-[var(--accent-primary)]'
                        : 'text-[var(--text-secondary)]'}
                    `}
                  >
                    <span className="text-[var(--text-muted)] mr-1">{rec.type}</span>
                    {rec.id.slice(0, 8)}...
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* CENTER PANEL — VEDA CONVERSATION */}
        <div className="flex flex-col flex-1 overflow-hidden">

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            {messages.length === 0 && !isLoading && (
              <div className="flex flex-col items-center justify-center h-full gap-3">
                <div className="w-10 h-10 rounded bg-[var(--accent-primary)] flex items-center justify-center">
                  <span className="text-white font-bold text-lg">V</span>
                </div>
                <p className="text-[var(--text-secondary)] text-sm">
                  VEDA is ready. Ask me anything.
                </p>
                <div className="flex flex-wrap gap-2 justify-center mt-2">
                  {["Show all employees", "Run payroll", "Pending approvals"].map(hint => (
                    <button
                      key={hint}
                      onClick={() => handleHintClick(hint)}
                      className="px-3 py-1.5 rounded border border-[var(--border-default)] text-[var(--text-secondary)] text-xs hover:border-[var(--border-active)] hover:text-[var(--text-primary)] transition-colors"
                    >
                      {hint}
                    </button>
                  ))}
                </div>
              </div>
            )}

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
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 rounded bg-[var(--accent-primary)] flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-xs font-bold">V</span>
                </div>
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)] animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
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
                onKeyDown={handleKeyDown}
                placeholder={isLoading ? 'VEDA is thinking...' : 'Ask VEDA anything...'}
                disabled={isLoading}
                className="flex-1 bg-transparent text-[var(--text-primary)] text-xs outline-none placeholder:text-[var(--text-muted)] disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={isLoading || !inputValue.trim()}
                className="text-[var(--text-muted)] hover:text-[var(--text-primary)] disabled:opacity-30 transition-colors"
              >
                <Send size={14} />
              </button>
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
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {activeContext.open_record_type ? (
              <div className="space-y-2">
                <p className="text-[var(--text-secondary)] text-xs font-medium uppercase tracking-wider">
                  Active Record
                </p>
                <div className="space-y-1">
                  <div className="flex gap-2">
                    <span className="text-[var(--text-muted)] text-xs w-16">Type</span>
                    <span className="text-[var(--text-primary)] text-xs">
                      {activeContext.open_record_type}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-[var(--text-muted)] text-xs w-16">ID</span>
                    <span className="text-[var(--text-primary)] text-xs font-mono truncate">
                      {activeContext.open_record_id?.slice(0, 8)}...
                    </span>
                  </div>
                  {activeContext.open_module && (
                    <div className="flex gap-2">
                      <span className="text-[var(--text-muted)] text-xs w-16">Module</span>
                      <span className="text-[var(--text-primary)] text-xs">
                        {activeContext.open_module}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-[var(--text-muted)] text-xs">
                No record open. Click a table row to open a record.
              </p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
