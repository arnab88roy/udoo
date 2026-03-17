'use client';
import { VEDAMessage as VEDAMessageType, UIAction } from '@/types/ui-response';
import { VEDACard } from './VEDACard';

interface Props {
  msg: VEDAMessageType;
  onAction?: (action: UIAction) => void;
  onRowClick?: (recordType: string, recordId: string) => void;
  onHintClick?: (hint: string) => void;
}

export function VEDAMessageBubble({ msg, onAction, onRowClick, onHintClick }: Props) {
  const isUser = msg.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {!isUser && (
        <div className="flex-shrink-0 w-6 h-6 rounded bg-[var(--accent-primary)] flex items-center justify-center mr-2 mt-0.5">
          <span className="text-white text-xs font-bold">V</span>
        </div>
      )}
      <div className={`max-w-[85%] ${isUser ? 'max-w-[60%]' : ''}`}>
        {isUser ? (
          <div className="bg-[var(--bg-input)] border border-[var(--border-default)] rounded px-3 py-2 text-xs text-[var(--text-primary)]">
            {msg.content}
          </div>
        ) : (
          <div>
            <p className="text-xs text-[var(--text-primary)] leading-relaxed">{msg.content}</p>
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
