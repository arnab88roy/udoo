'use client';
import { ApprovalPayload, UIAction } from '@/types/ui-response';
import { ActionButton } from './ActionButton';

interface Props {
  payload: ApprovalPayload;
  actions?: UIAction[];
  onAction?: (action: UIAction) => void;
}

export function ApprovalCard({ payload, actions, onAction }: Props) {
  return (
    <div className="rounded border border-yellow-500/50 bg-card mt-2 overflow-hidden">
      <div className="px-3 py-2 bg-yellow-500/10 border-b border-yellow-500/50 flex items-center gap-2">
        <span className="text-yellow-600 dark:text-yellow-400 text-xs font-medium uppercase tracking-wider">
          ⚑ Approval Required — {payload.record_type.replace(/_/g, ' ')}
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
