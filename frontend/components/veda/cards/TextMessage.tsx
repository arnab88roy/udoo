'use client';
import { TextPayload } from '@/types/ui-response';

interface Props {
  payload: TextPayload;
  onHintClick?: (hint: string) => void;
}

export function TextMessage({ payload, onHintClick }: Props) {
  return (
    <div className="mt-1">
      <p className="text-[var(--text-primary)] text-xs leading-relaxed whitespace-pre-wrap">
        {payload.content}
      </p>
      {payload.hints.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {payload.hints.map(hint => (
            <button
              key={hint}
              onClick={() => onHintClick?.(hint)}
              className="px-2 py-1 rounded border border-[var(--border-default)] text-[var(--text-secondary)] text-xs hover:border-[var(--border-active)] hover:text-[var(--text-primary)] transition-colors"
            >
              {hint}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
