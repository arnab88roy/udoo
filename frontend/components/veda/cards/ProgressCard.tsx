'use client';
import { ProgressPayload } from '@/types/ui-response';

const STATUS_ICONS: Record<string, string> = {
  pending: '○',
  in_progress: '◎',
  completed: '●',
  failed: '✕',
  skipped: '—',
};

const STATUS_CLASSES: Record<string, string> = {
  pending: 'text-muted-foreground',
  in_progress: 'text-blue-500',
  completed: 'text-green-500',
  failed: 'text-destructive',
  skipped: 'text-muted-foreground',
};

interface Props { payload: ProgressPayload; }

export function ProgressCard({ payload }: Props) {
  return (
    <div className="rounded border border-border bg-card mt-2 overflow-hidden">
      <div className="px-3 py-2 border-b border-border flex items-center justify-between">
        <span className="text-muted-foreground text-xs uppercase tracking-wider">Progress</span>
        <span className="text-muted-foreground text-xs">{payload.percent}%</span>
      </div>
      <div className="p-3 space-y-2">
        {payload.steps.map((step, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className={`text-xs mt-0.5 ${STATUS_CLASSES[step.status] ?? 'text-muted-foreground'}`}>
              {STATUS_ICONS[step.status] ?? '○'}
            </span>
            <div>
              <p className="text-xs text-foreground">{step.label}</p>
              {step.detail && (
                <p className="text-xs text-muted-foreground mt-0.5">{step.detail}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
