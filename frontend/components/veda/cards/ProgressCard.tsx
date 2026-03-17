'use client';
import { ProgressPayload } from '@/types/ui-response';

const STATUS_ICONS: Record<string, string> = {
  pending: '○',
  in_progress: '◎',
  completed: '●',
  failed: '✕',
  skipped: '—',
};

const STATUS_COLORS: Record<string, string> = {
  pending: 'var(--text-muted)',
  in_progress: 'var(--accent-info)',
  completed: 'var(--accent-success)',
  failed: 'var(--accent-danger)',
  skipped: 'var(--text-muted)',
};

interface Props { payload: ProgressPayload; }

export function ProgressCard({ payload }: Props) {
  return (
    <div className="rounded border border-[var(--border-default)] bg-[var(--bg-card)] mt-2 overflow-hidden">
      <div className="px-3 py-2 border-b border-[var(--border-subtle)] flex items-center justify-between">
        <span className="text-[var(--text-secondary)] text-xs uppercase tracking-wider">Progress</span>
        <span className="text-[var(--text-secondary)] text-xs">{payload.percent}%</span>
      </div>
      <div className="p-3 space-y-2">
        {payload.steps.map((step, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className="text-xs mt-0.5" style={{ color: STATUS_COLORS[step.status] }}>
              {STATUS_ICONS[step.status]}
            </span>
            <div>
              <p className="text-xs text-[var(--text-primary)]">{step.label}</p>
              {step.detail && (
                <p className="text-xs text-[var(--text-muted)] mt-0.5">{step.detail}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
