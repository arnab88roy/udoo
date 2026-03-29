'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, X, ChevronDown, ListFilter } from 'lucide-react';
import { VEDAMessageBubble } from '@/components/veda/VEDAMessage';
import { VEDAMessage, UIAction, UIContext, UserRole } from '@/types/ui-response';
import { VEDAMode } from '@/lib/design-system';
import { sendVEDAMessage, executeAction as vedaExecuteAction } from '@/lib/veda-client';

interface VEDAPanelProps {
  activeContext: UIContext;
  setActiveContext: (ctx: UIContext) => void;
  onRowClick: (type: string, id: string) => void;
  userRole: UserRole;
  userName: string;
  vedaMode: VEDAMode;
  onVEDAModeChange: (mode: VEDAMode) => void;
  onCollapse: () => void;
}

let messageIdCounter = 0;
function nextId() { return String(++messageIdCounter); }

export function VEDAPanel({ 
  activeContext, 
  setActiveContext, 
  onRowClick, 
  userRole, 
  userName, 
  vedaMode, 
  onVEDAModeChange,
  onCollapse 
}: VEDAPanelProps) {
  const [messages, setMessages] = useState<VEDAMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showModeDropdown, setShowModeDropdown] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const buildHistory = () => {
    return messages
      .slice(-10)
      .map(m => ({
        role: m.role === 'assistant' ? 'assistant' : 'user',
        content: m.content,
      }));
  };

  const handleSend = async () => {
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
  };

  const handleAction = async (action: UIAction) => {
    if (!action.endpoint) return;

    try {
      const result = await vedaExecuteAction(
        action.endpoint,
        action.method,
        action.payload || {},
      );

      if (result.ok) {
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
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-(--bg-panel)/80 backdrop-blur-3xl border-l border-(--border-subtle) overflow-hidden relative shadow-2xl z-30">
      
      {/* Header */}
      <div className="px-4 h-14 border-b border-(--border-subtle) flex items-center justify-between shrink-0 bg-(--bg-panel)/50 backdrop-blur-sm">
        <div className="flex items-center gap-2">
           <div className="w-2 h-2 rounded-full bg-(--veda-purple) animate-pulse shadow-(--veda-glow)" />
           <span className="text-(--text-primary) text-[11px] font-black uppercase tracking-widest leading-none">
             VEDA Co-pilot
           </span>
        </div>

        {/* Mode Switcher */}
        <div className="relative">
          <button 
            onClick={() => setShowModeDropdown(!showModeDropdown)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-(--bg-panel-hover) border border-(--border-subtle) text-[10px] font-bold tracking-tighter hover:bg-(--bg-panel-hover)/80 transition-all"
          >
            <span className={vedaMode === 'veda-auto' ? 'text-(--veda-purple)' : 'text-(--text-primary)'}>
              {vedaMode === 'veda-auto' ? 'AUTO' : 'ASSIST'}
            </span>
            <ChevronDown size={10} className="text-(--text-muted)" />
          </button>

          {showModeDropdown && (
            <div className="absolute right-0 top-full mt-1 w-32 bg-(--bg-panel) border border-(--border-subtle) rounded-xl shadow-2xl z-50 p-1 animate-in fade-in slide-in-from-top-1 duration-200">
              <button 
                onClick={() => { onVEDAModeChange('veda-auto'); setShowModeDropdown(false); }}
                className={`w-full text-left px-3 py-2 rounded-lg text-[10px] font-bold mb-0.5 transition-colors ${vedaMode === 'veda-auto' ? 'bg-(--veda-purple) text-white' : 'text-(--text-secondary) hover:bg-(--bg-panel-hover)'}`}
              >
                AUTO
              </button>
              <button 
                onClick={() => { onVEDAModeChange('veda-assist'); setShowModeDropdown(false); }}
                className={`w-full text-left px-3 py-2 rounded-lg text-[10px] font-bold transition-colors ${vedaMode === 'veda-assist' ? 'bg-(--veda-purple) text-white' : 'text-(--text-secondary) hover:bg-(--bg-panel-hover)'}`}
              >
                ASSIST
              </button>
            </div>
          )}
        </div>

        <button 
          onClick={onCollapse}
          className="text-(--text-muted) hover:text-(--text-primary) transition-all p-1.5 rounded-md hover:bg-(--bg-panel-hover)"
        >
          <X size={14} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth space-y-6 scrollbar-hide">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full gap-4 text-center opacity-40 animate-in fade-in zoom-in duration-500">
            <div className="w-12 h-12 rounded-2xl bg-(--bg-panel-hover) border border-(--border-subtle) flex items-center justify-center">
                <Sparkles size={24} className="text-(--veda-purple)" />
            </div>
            <div className="space-y-1">
                <p className="text-(--text-primary) text-xs font-bold uppercase tracking-widest">Awaiting Command</p>
                <p className="text-[11px] text-(--text-secondary) max-w-[200px]">Ask me to run modules or generate insights, {userName.split(' ')[0]}.</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <VEDAMessageBubble
            key={msg.id}
            msg={msg}
            onAction={handleAction}
            onRowClick={onRowClick}
            onHintClick={(hint) => setInputValue(hint)}
            compact={true}
          />
        ))}

        {isLoading && (
          <div className="flex items-start gap-3 animate-in fade-in duration-300">
            <div className="w-7 h-7 rounded-lg bg-(--veda-purple) flex items-center justify-center shrink-0 shadow-lg shadow-(--veda-glow)">
               <span className="text-white text-[8px] font-black uppercase tracking-tighter">VEDA</span>
            </div>
            <div className="px-4 py-2 rounded-2xl bg-linear-to-r from-(--veda-purple)/5 to-blue-500/5 border border-(--veda-purple-border)/20 text-[11px] font-bold text-(--veda-purple) tracking-widest uppercase flex items-center gap-1.5 animate-pulse">
                Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-(--bg-panel)/50 backdrop-blur-xl border-t border-(--border-subtle) shrink-0">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-linear-to-r from-(--veda-purple) to-blue-500 rounded-xl blur opacity-0 group-focus-within:opacity-20 transition-opacity duration-500" />
          <div className="relative flex items-center gap-2 bg-(--bg-base)/50 border border-(--border-subtle) rounded-xl px-3 py-2.5 shadow-xl transition-all duration-300 focus-within:border-(--veda-purple-border) focus-within:ring-1 ring-(--veda-purple-border)/20">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isLoading ? 'VEDA is thinking...' : 'Ask VEDA...'}
              disabled={isLoading}
              className="flex-1 bg-transparent text-[12px] font-medium text-(--text-primary) outline-none placeholder:text-(--text-muted)/50"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !inputValue.trim()}
              className="w-8 h-8 flex items-center justify-center rounded-lg bg-(--veda-purple) text-white hover:bg-violet-500 disabled:bg-(--border-subtle) disabled:text-(--text-muted) transition-all shadow-lg shadow-(--veda-glow)/20"
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
