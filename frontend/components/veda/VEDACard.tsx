'use client';
import { UIResponse, UIAction } from '@/types/ui-response';
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

  switch (type) {
    case 'table':
      return (
        <InlineTable
          payload={payload as any}
          actions={actions}
          onRowClick={(id) => onRowClick?.(
            (payload as any).record_type ?? 'record', id
          )}
          onAction={onAction}
        />
      );
    case 'form':
      return <InlineForm payload={payload as any} actions={actions} onAction={onAction} />;
    case 'approval':
      return <ApprovalCard payload={payload as any} actions={actions} onAction={onAction} />;
    case 'blocker':
      return <BlockerCard payload={payload as any} onAction={onAction} />;
    case 'confirm':
      return <ConfirmCard payload={payload as any} actions={actions} onAction={onAction} />;
    case 'progress':
      return <ProgressCard payload={payload as any} />;
    case 'text':
      return <TextMessage payload={payload as any} onHintClick={onHintClick} />;
    default:
      return null;
  }
}
