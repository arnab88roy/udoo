'use client';
import { BlockerPayload, UIAction } from '@/types/ui-response';
import { ActionButton } from './ActionButton';

interface Props {
  payload: BlockerPayload;
  onAction?: (action: UIAction) => void;
}

export function BlockerCard({ payload, onAction }: Props) {
  return (
    <div className="rounded border border-[var(--accent-danger)] bg-[var(--bg-card)] mt-2 overflow-hidden">
      <div className="px-3 py-2 bg-[rgba(158,61,61,0.1)] border-b border-[var(--accent-danger)] flex items-center gap-2">
        <span className="text-[var(--accent-danger)] text-xs font-medium uppercase tracking-wider">
          ✕ Blocked{payload.blocked_task ? ` — ${payload.blocked_task}` : ''}
        </span>
      </div>
      <p className="px-3 py-3 text-[var(--text-primary)] text-xs leading-relaxed">
        {payload.reason}
      </p>
      {payload.resolution_options.length > 0 && (
        <div className="flex gap-2 px-3 py-2 border-t border-[var(--border-subtle)]">
          {payload.resolution_options.map(action => (
            <ActionButton key={action.action_id} action={action} onAction={onAction} />
          ))}
        </div>
      )}
    </div>
  );
}
