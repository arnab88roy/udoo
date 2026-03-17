import { UIResponse, UIContext } from '@/types/ui-response';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const TOKEN = process.env.NEXT_PUBLIC_VEDA_TOKEN || '';
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || '';

export interface VEDARequestPayload {
  message: string;
  context: UIContext;
  conversation_history: { role: string; content: string }[];
}

export async function sendVEDAMessage(
  payload: VEDARequestPayload
): Promise<UIResponse> {
  const response = await fetch(`${API_URL}/api/veda/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${TOKEN}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`VEDA API error ${response.status}: ${error}`);
  }

  return response.json();
}

export function buildNullContext(): UIContext {
  return {
    open_record_type: null,
    open_record_id: null,
    open_module: null,
    tenant_id: TENANT_ID,
  };
}
