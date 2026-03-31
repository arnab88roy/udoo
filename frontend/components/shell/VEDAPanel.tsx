'use client';
import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, X, ChevronDown, Bot, Sparkle, PanelRightClose } from 'lucide-react';
import { VEDAMessageBubble } from '@/components/veda/VEDAMessage';
import { VEDAMessage, UIAction, UIContext, UserRole } from '@/types/ui-response';
import { VEDAMode } from '@/types/shell';
import { sendVEDAMessage, executeAction as vedaExecuteAction } from '@/lib/veda-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

interface VEDAPanelProps {
  activeContext: UIContext;
  setActiveContext: (ctx: UIContext) => void;
  onRowClick: (type: string, id: string) => void;
  userRole: UserRole;
  userName: string;
  vedaMode: VEDAMode;
  onVEDAModeChange: (mode: VEDAMode) => void;
  isVEDAOpen?: boolean;
  onToggleVEDA?: () => void;
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
  onToggleVEDA 
}: VEDAPanelProps) {
  const [messages, setMessages] = useState<VEDAMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
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
      }
    } catch (err) {
        console.error('Action execution failed', err);
        const errorMsg: VEDAMessage = {
          id: nextId(),
          role: 'assistant',
          content: 'The action failed to execute.',
          response: {
            type: 'blocker',
            message: 'The action failed to execute.',
            payload: {
              reason: err instanceof Error ? err.message : 'Unknown error',
              resolution_options: [],
              blocked_task: action.label,
            },
            actions: [],
            context: activeContext,
          },
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMsg]);
        setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-transparent overflow-hidden relative z-30">

      
      {/* Header */}
      <div className="px-4 h-12 flex items-center justify-between shrink-0 bg-transparent">
        <div className="flex items-center gap-2">
           <div className="relative">
              <Sparkle className="h-4 w-4 text-primary animate-pulse" />
              <div className="absolute inset-0 bg-primary/20 blur-md rounded-full" />
           </div>
           <span className="text-glass-fg-secondary text-[10px] font-bold uppercase tracking-widest leading-none">
             Assistant
           </span>
        </div>


        {/* Mode & Actions — Simplified: Toggle is now handled by the Shell Rail */}
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="h-7 px-2 text-[10px] font-bold bg-background/50 border-white/10 text-glass-fg-primary hover:bg-white/10">
                <span className={cn(vedaMode === 'auto' ? "text-primary" : "text-glass-fg-inactive")}>
                  {vedaMode.toUpperCase()}
                </span>
                <ChevronDown className="ml-1 h-3 w-3 opacity-50" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-32 bg-popover/80 backdrop-blur-md border-white/10">
              <DropdownMenuItem onClick={() => onVEDAModeChange('auto')} className="text-xs">
                Auto
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onVEDAModeChange('assist')} className="text-xs">
                Assist
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {onToggleVEDA && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggleVEDA}
              className="h-7 w-7 text-glass-fg-inactive hover:text-glass-fg-primary hover:bg-white/10"
            >
              <PanelRightClose className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* 2. Content Area — The White Sheet Starts Here */}
      <div className="flex-1 flex flex-col overflow-hidden bg-sheet shadow-sheet rounded-2xl">
        {/* Messages Window */}
        <ScrollArea className="flex-1 px-4">
        <div className="py-6 flex flex-col gap-6 min-h-full">
          {messages.length === 0 && !isLoading && (
            <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center opacity-100 animate-in fade-in zoom-in duration-500 py-12">
              <div className="w-12 h-12 rounded-2xl bg-white/10 border border-white/10 flex items-center justify-center">
                  <Bot size={24} className="text-primary" />
              </div>
              <div className="space-y-1">
                  <p className="text-glass-fg-primary text-xs font-bold uppercase tracking-widest">System Ready</p>
                  <p className="text-[11px] text-glass-fg-secondary max-w-[180px]">Ask VEDA for support with {(userName || 'your').split(' ')[0]}&apos;s workspace.</p>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <VEDAMessageBubble
              key={msg.id}
              msg={msg}
              onAction={vedaMode === 'auto' ? handleAction : undefined}
              onRowClick={onRowClick}
              onHintClick={(hint) => setInputValue(hint)}
              compact={true}
            />
          ))}

          {isLoading && (
            <div className="flex items-start gap-3 animate-in fade-in duration-300">
              <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center shrink-0 shadow-sm">
                 <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
              <Badge variant="outline" className="px-3 py-1 text-[10px] font-bold text-primary tracking-widest uppercase animate-pulse">
                  VEDA is thinking...
              </Badge>
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>
      </ScrollArea>

      {/* Input Stage */}
      <div className="p-4 bg-transparent shrink-0">
        <div className="relative flex items-center gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isLoading ? 'VEDA is thinking...' : 'Ask VEDA...'}
            disabled={isLoading}
            className="h-10 pl-3 pr-10 text-[12px] font-medium bg-background/50 border-muted focus-visible:ring-1"
          />
          <Button
            size="icon"
            onClick={handleSend}
            disabled={isLoading || !inputValue.trim()}
            className="absolute right-1 h-8 w-8 bg-primary hover:bg-primary/90 text-primary-foreground transition-all shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  </div>
  );
}



