'use client';
import { TablePayload, UIAction } from '@/types/ui-response';
import { ActionButton } from './ActionButton';

interface Props {
  payload: TablePayload;
  actions?: UIAction[];
  onRowClick?: (recordId: string) => void;
  onAction?: (action: UIAction) => void;
}

export function InlineTable({ payload, actions, onRowClick, onAction }: Props) {
  const { columns, column_labels, rows, total, record_type, row_id_field = 'id' } = payload;

  return (
    <div className="rounded border border-[var(--border-default)] overflow-hidden mt-2">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-[var(--bg-panel)] border-b border-[var(--border-subtle)]">
              {columns.map(col => (
                <th
                  key={col}
                  className="text-left px-3 py-2 text-[var(--text-secondary)] font-medium uppercase tracking-wider"
                >
                  {column_labels?.[col] ?? col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                onClick={() => record_type && onRowClick?.(String(row[row_id_field]))}
                className={`
                  border-b border-[var(--border-subtle)] last:border-0
                  ${record_type ? 'cursor-pointer hover:bg-[var(--bg-panel-hover)]' : ''}
                  transition-colors
                `}
              >
                {columns.map(col => (
                  <td key={col} className="px-3 py-2 text-[var(--text-primary)]">
                    {String(row[col] ?? '—')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-3 py-2 bg-[var(--bg-panel)] border-t border-[var(--border-subtle)]">
        <span className="text-[var(--text-muted)] text-xs">{total} records</span>
        {actions && actions.length > 0 && (
          <div className="flex gap-2">
            {actions.map(action => (
              <ActionButton key={action.action_id} action={action} onAction={onAction} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
