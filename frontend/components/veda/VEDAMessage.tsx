'use client';
import { VEDAMessage as VEDAMessageType, UIAction } from '@/types/ui-response';
import { VEDACard } from './VEDACard';

interface Props {
  msg: VEDAMessageType;
  onAction?: (action: UIAction) => void;
  onRowClick?: (recordType: string, recordId: string) => void;
  onHintClick?: (hint: string) => void;
  compact?: boolean;
}

export function VEDAMessageBubble({ msg, onAction, onRowClick, onHintClick, compact }: Props) {
  const isUser = msg.role === 'user';

  if (compact) {
    return (
      <div className={`flex flex-col gap-1 mb-3 animate-in slide-in-from-bottom-2 duration-300 ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`max-w-[90%] px-3 py-2 rounded-xl text-[11px] leading-snug shadow-sm ${
          isUser
            ? 'bg-primary text-primary-foreground rounded-tr-none'
            : 'bg-muted border border-border text-foreground rounded-tl-none'
        }`}>
          {msg.content}
        </div>
        {msg.response && (
           <div className="w-full mt-1">
              <VEDACard
                response={msg.response}
                onAction={onAction}
                onRowClick={onRowClick}
                onHintClick={onHintClick}
              />
           </div>
        )}
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 group animate-in fade-in duration-300`}>
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-lg bg-linear-to-tr from-primary to-blue-500 flex items-center justify-center mr-3 mt-0.5 shadow-md transform group-hover:scale-110 transition-transform">
          <span className="text-white text-[10px] font-bold uppercase tracking-tighter">VEDA</span>
        </div>
      )}
      <div className={`max-w-[85%] ${isUser ? 'max-w-[75%]' : ''}`}>
        {isUser ? (
          <div className="bg-muted border border-border rounded-2xl px-5 py-3 text-sm text-foreground shadow-sm hover:shadow-md transition-shadow">
            {msg.content}
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-foreground leading-relaxed bg-card/40 rounded-2xl p-4 border border-border/50">
              {msg.content}
            </p>
            {msg.response && (
              <VEDACard
                response={msg.response}
                onAction={onAction}
                onRowClick={onRowClick}
                onHintClick={onHintClick}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
