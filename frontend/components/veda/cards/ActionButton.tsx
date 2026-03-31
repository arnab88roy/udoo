'use client';
import { UIAction } from '@/types/ui-response';

const STYLE_CLASSES: Record<string, string> = {
  primary: 'bg-primary text-primary-foreground hover:opacity-90',
  secondary: 'border border-border text-muted-foreground hover:border-ring hover:text-foreground',
  danger: 'bg-destructive text-destructive-foreground hover:opacity-90',
  ghost: 'text-muted-foreground hover:text-foreground',
};

interface Props {
  action: UIAction;
  onAction?: (action: UIAction) => void;
}

export function ActionButton({ action, onAction }: Props) {
  return (
    <button
      onClick={() => onAction?.(action)}
      className={`px-3 py-1 rounded text-xs font-medium transition-all ${STYLE_CLASSES[action.style] ?? STYLE_CLASSES.secondary}`}
    >
      {action.label}
    </button>
  );
}
