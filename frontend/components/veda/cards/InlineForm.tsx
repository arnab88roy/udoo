'use client';
import { useState } from 'react';
import { FormPayload, UIAction } from '@/types/ui-response';
import { ActionButton } from './ActionButton';

interface Props {
  payload: FormPayload;
  actions?: UIAction[];
  onAction?: (action: UIAction) => void;
}

export function InlineForm({ payload, actions, onAction }: Props) {
  const [values, setValues] = useState<Record<string, unknown>>(payload.values);

  const handleChange = (name: string, value: string) => {
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const handleAction = (action: UIAction) => {
    // Merge current form values into the action payload before dispatching
    const enriched: UIAction = {
      ...action,
      payload: { ...action.payload, ...values },
    };
    onAction?.(enriched);
  };

  return (
    <div className="rounded border border-border bg-card mt-2 overflow-hidden">
      <div className="px-3 py-2 border-b border-border">
        <span className="text-muted-foreground text-xs uppercase tracking-wider">
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
                ? 'border-l-2 border-primary pl-2'
                : ''
            }`}
          >
            <label className="block text-muted-foreground text-xs mb-1 flex items-center gap-1">
              <span>{field.label}</span>
              {field.required && (
                <span className="text-destructive">*</span>
              )}
              {field.veda_filled && (
                <span className="text-primary text-xs ml-1">VEDA</span>
              )}
              {field.veda_filled && field.veda_confidence != null && field.veda_confidence < 0.8 && (
                <span className="text-yellow-600 text-xs">⚠ Review</span>
              )}
            </label>
            {field.readonly ? (
              <p className="text-muted-foreground text-xs py-1">
                {String(payload.values[field.name] ?? '—')}
              </p>
            ) : (
              <input
                type="text"
                value={String(values[field.name] ?? '')}
                onChange={(e) => handleChange(field.name, e.target.value)}
                placeholder={field.placeholder ?? ''}
                className={`
                  w-full border border-border rounded px-2 py-1
                  text-xs text-foreground focus:outline-none
                  focus:border-ring transition-colors
                  ${field.veda_filled
                    ? 'bg-primary/5'
                    : 'bg-background'}
                `}
              />
            )}
          </div>
        ))}
      </div>
      {actions && actions.length > 0 && (
        <div className="flex gap-2 px-3 py-2 border-t border-border">
          {actions.map(action => (
            <ActionButton key={action.action_id} action={action} onAction={handleAction} />
          ))}
        </div>
      )}
    </div>
  );
}
