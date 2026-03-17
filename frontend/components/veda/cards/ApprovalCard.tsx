'use client';
import { ApprovalPayload, UIAction } from '@/types/ui-response';
import { ActionButton } from './ActionButton';

interface Props {
  payload: ApprovalPayload;
  actions: UIAction[];
  onAction?: (action: UIAction) => void;
}

export function ApprovalCard({ payload, actions, onAction }: Props) {
  return (
    <div className="rounded border border-[var(--accent-warning)] bg-[var(--bg-card)] mt-2 overflow-hidden">
      <div className="px-3 py-2 bg-[rgba(184,134,11,0.1)] border-b border-[var(--accent-warning)] flex items-center gap-2">
        <span className="text-[var(--accent-warning)] text-xs font-medium uppercase tracking-wider">
          ⚑ Approval Required — {payload.record_type.replace(/_/g, ' ')}
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
      <div className="flex gap-2 px-3 py-2 border-t border-[var(--border-subtle)]">
        {actions.map(action => (
          <ActionButton key={action.action_id} action={action} onAction={onAction} />
        ))}
      </div>
    </div>
  );
}
