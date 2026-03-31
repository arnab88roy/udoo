'use client';
import { ConfirmPayload, UIAction } from '@/types/ui-response';
import { ActionButton } from './ActionButton';

interface Props {
  payload: ConfirmPayload;
  actions?: UIAction[];
  onAction?: (action: UIAction) => void;
}

export function ConfirmCard({ payload, actions, onAction }: Props) {
  return (
    <div className="rounded border border-blue-500/50 bg-card mt-2 overflow-hidden">
      <div className="px-3 py-2 bg-blue-500/10 border-b border-blue-500/50">
        <span className="text-blue-600 dark:text-blue-400 text-xs font-medium uppercase tracking-wider">
          ◈ Confirm Action
        </span>
      </div>
      <div className="p-3 grid grid-cols-2 gap-x-6 gap-y-1">
        {Object.entries(payload.summary).map(([k, v]) => (
          <div key={k} className="flex gap-2">
            <span className="text-muted-foreground text-xs min-w-[80px]">{k}</span>
            <span className="text-foreground text-xs">{v}</span>
          </div>
        ))}
      </div>
      {payload.warning && (
        <p className="mx-3 mb-2 px-2 py-1 bg-yellow-500/10 border border-yellow-500/50 rounded text-yellow-600 dark:text-yellow-400 text-xs">
          ⚠ {payload.warning}
        </p>
      )}
      {payload.is_irreversible && (
        <p className="mx-3 mb-2 px-2 py-1 bg-destructive/10 border border-destructive/50 rounded text-destructive text-xs">
          ✕ This cannot be undone.
        </p>
      )}
      {actions && actions.length > 0 && (
        <div className="flex gap-2 px-3 py-2 border-t border-border">
          {actions.map(action => (
            <ActionButton key={action.action_id} action={action} onAction={onAction} />
          ))}
        </div>
      )}
    </div>
  );
}
