'use client';
import { FormPayload, UIAction } from '@/types/ui-response';
import { ActionButton } from './ActionButton';

interface Props {
  payload: FormPayload;
  actions?: UIAction[];
  onAction?: (action: UIAction) => void;
}

export function InlineForm({ payload, actions, onAction }: Props) {
  return (
    <div className="rounded border border-[var(--border-default)] bg-[var(--bg-card)] mt-2 overflow-hidden">
      <div className="px-3 py-2 border-b border-[var(--border-subtle)]">
        <span className="text-[var(--text-secondary)] text-xs uppercase tracking-wider">
          {payload.record_type.replace(/_/g, ' ')}
          {payload.record_id ? ` — Edit` : ` — New`}
        </span>
      </div>
      <div className="p-3 grid grid-cols-2 gap-3">
        {payload.fields.map(field => (
          <div
            key={field.name}
            className={`${
              field.veda_filled
                ? 'border-l-2 border-[var(--veda-purple)] pl-2'
                : ''
            }`}
          >
            <label className="block text-[var(--text-secondary)] text-xs mb-1 flex items-center gap-1">
              <span>{field.label}</span>
              {field.required && (
                <span className="text-[var(--accent-danger)]">*</span>
              )}
              {field.veda_filled && (
                <span className="text-[var(--veda-purple)] text-xs ml-1">VEDA</span>
              )}
              {field.veda_filled && field.veda_confidence !== null &&
               field.veda_confidence !== undefined && field.veda_confidence < 0.8 && (
                <span className="text-[var(--accent-warning)] text-xs">⚠ Review</span>
              )}
            </label>
            {field.readonly ? (
              <p className="text-[var(--text-muted)] text-xs py-1">
                {String(payload.values[field.name] ?? '—')}
              </p>
            ) : (
              <input
                type="text"
                defaultValue={String(payload.values[field.name] ?? '')}
                placeholder={field.placeholder ?? ''}
                className={`
                  w-full border border-[var(--border-default)] rounded px-2 py-1
                  text-xs text-[var(--text-primary)] focus:outline-none
                  focus:border-[var(--border-active)] transition-colors
                  ${field.veda_filled
                    ? 'bg-[var(--veda-purple-bg)]'
                    : 'bg-[var(--bg-input)]'}
                `}
              />
            )}
          </div>
        ))}
      </div>
      {actions && actions.length > 0 && (
        <div className="flex gap-2 px-3 py-2 border-t border-[var(--border-subtle)]">
          {actions.map(action => (
            <ActionButton key={action.action_id} action={action} onAction={onAction} />
          ))}
        </div>
      )}
    </div>
  );
}
