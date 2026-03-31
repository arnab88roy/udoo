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
    <div className="rounded border border-border overflow-hidden mt-2">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-muted border-b border-border">
              {columns.map(col => (
                <th
                  key={col}
                  className="text-left px-3 py-2 text-muted-foreground font-medium uppercase tracking-wider"
                >
                  {column_labels?.[col] ?? col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => {
              const rowId = row[row_id_field];
              return (
                <tr
                  key={rowId != null ? String(rowId) : i}
                  onClick={() => record_type && rowId != null && onRowClick?.(String(rowId))}
                  className={`
                    border-b border-border last:border-0
                    ${record_type ? 'cursor-pointer hover:bg-muted/50' : ''}
                    transition-colors
                  `}
                >
                  {columns.map(col => (
                    <td key={`${i}-${col}`} className="px-3 py-2 text-foreground">
                      {String(row[col] ?? '—')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-3 py-2 bg-muted border-t border-border">
        <span className="text-muted-foreground text-xs">{total} records</span>
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
