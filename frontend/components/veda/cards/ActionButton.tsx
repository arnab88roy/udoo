'use client';
import { UIAction } from '@/types/ui-response';

const STYLE_CLASSES: Record<string, string> = {
  primary: 'bg-[var(--accent-primary)] text-white hover:opacity-90',
  secondary: 'border border-[var(--border-default)] text-[var(--text-secondary)] hover:border-[var(--border-active)] hover:text-[var(--text-primary)]',
  danger: 'bg-[var(--accent-danger)] text-white hover:opacity-90',
  ghost: 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]',
};

interface Props {
  action: UIAction;
  onAction?: (action: UIAction) => void;
}

export function ActionButton({ action, onAction }: Props) {
  return (
    <button
      onClick={() => onAction?.(action)}
      className={`px-3 py-1 rounded text-xs font-medium transition-all ${STYLE_CLASSES[action.style]}`}
    >
      {action.label}
    </button>
  );
}
