'use client';
import {
  UIResponse, UIAction,
  TablePayload, FormPayload, ApprovalPayload, BlockerPayload,
  ConfirmPayload, ProgressPayload, TextPayload,
} from '@/types/ui-response';
import {
  InlineTable,
  InlineForm,
  ApprovalCard,
  BlockerCard,
  ConfirmCard,
  ProgressCard,
  TextMessage
} from './cards';

interface Props {
  response: UIResponse;
  onAction?: (action: UIAction) => void;
  onRowClick?: (recordType: string, recordId: string) => void;
  onHintClick?: (hint: string) => void;
}

export function VEDACard({ response, onAction, onRowClick, onHintClick }: Props) {
  const { type, payload, actions } = response;
  if (!payload) return null;

  switch (type) {
    case 'table': {
      const p = payload as TablePayload;
      return (
        <InlineTable
          payload={p}
          actions={actions}
          onRowClick={(id) => onRowClick?.(p.record_type ?? 'record', id)}
          onAction={onAction}
        />
      );
    }
    case 'form':
      return <InlineForm payload={payload as FormPayload} actions={actions} onAction={onAction} />;
    case 'approval':
      return <ApprovalCard payload={payload as ApprovalPayload} actions={actions} onAction={onAction} />;
    case 'blocker':
      return <BlockerCard payload={payload as BlockerPayload} onAction={onAction} />;
    case 'confirm':
      return <ConfirmCard payload={payload as ConfirmPayload} actions={actions} onAction={onAction} />;
    case 'progress':
      return <ProgressCard payload={payload as ProgressPayload} />;
    case 'text':
      return <TextMessage payload={payload as TextPayload} onHintClick={onHintClick} />;
    default:
      return null;
  }
}
