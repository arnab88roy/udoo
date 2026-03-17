'use client';
import { ConfirmPayload, UIAction } from '@/types/ui-response';
import { ActionButton } from './ActionButton';

interface Props {
  payload: ConfirmPayload;
  actions: UIAction[];
  onAction?: (action: UIAction) => void;
}

export function ConfirmCard({ payload, actions, onAction }: Props) {
  return (
    <div className="rounded border border-[var(--accent-info)] bg-[var(--bg-card)] mt-2 overflow-hidden">
      <div className="px-3 py-2 bg-[rgba(61,107,158,0.1)] border-b border-[var(--accent-info)]">
        <span className="text-[var(--accent-info)] text-xs font-medium uppercase tracking-wider">
          ◈ Confirm Action
        </span>
      </div>
      <div className="p-3 grid grid-cols-2 gap-x-6 gap-y-1">
        {Object.entries(payload.summary).map(([k, v]) => (
          <div key={k} className="flex gap-2">
            <span className="text-[var(--text-secondary)] text-xs min-w-[80px]">{k}</span>
            <span className="text-[var(--text-primary)] text-xs">{v}</span>
          </div>
        ))}
      </div>
      {payload.warning && (
        <p className="mx-3 mb-2 px-2 py-1 bg-[rgba(184,134,11,0.1)] border border-[var(--accent-warning)] rounded text-[var(--accent-warning)] text-xs">
          ⚠ {payload.warning}
        </p>
      )}
      {payload.is_irreversible && (
        <p className="mx-3 mb-2 px-2 py-1 bg-[rgba(158,61,61,0.1)] border border-[var(--accent-danger)] rounded text-[var(--accent-danger)] text-xs">
          ✕ This cannot be undone.
        </p>
      )}
      <div className="flex gap-2 px-3 py-2 border-t border-[var(--border-subtle)]">
        {actions.map(action => (
          <ActionButton key={action.action_id} action={action} onAction={onAction} />
        ))}
      </div>
    </div>
  );
}
