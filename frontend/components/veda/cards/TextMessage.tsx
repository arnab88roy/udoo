'use client';
import { TextPayload } from '@/types/ui-response';

interface Props {
  payload: TextPayload;
  onHintClick?: (hint: string) => void;
}

export function TextMessage({ payload, onHintClick }: Props) {
  return (
    <div className="mt-1">
      <p className="text-foreground text-xs leading-relaxed whitespace-pre-wrap">
        {payload.content}
      </p>
      {payload.hints.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {payload.hints.map((hint, i) => (
            <button
              key={`hint-${i}`}
              onClick={() => onHintClick?.(hint)}
              className="px-2 py-1 rounded border border-border text-muted-foreground text-xs hover:border-ring hover:text-foreground transition-colors"
            >
              {hint}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
