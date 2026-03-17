export type UIResponseType =
  | 'table' | 'form' | 'approval' | 'blocker'
  | 'confirm' | 'progress' | 'text';

export interface UIContext {
  open_record_type: string | null;
  open_record_id: string | null;
  open_module: string | null;
  tenant_id: string;
}

export interface UIAction {
  action_id: string;
  label: string;
  style: 'primary' | 'secondary' | 'danger' | 'ghost';
  endpoint: string;
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  payload: Record<string, unknown>;
  confirmation_required: boolean;
  sets_context?: Record<string, unknown> | null;
}

export interface TablePayload {
  columns: string[];
  column_labels?: Record<string, string>;
  rows: Record<string, unknown>[];
  total: number;
  page?: number;
  page_size?: number;
  record_type?: string | null;
  row_id_field?: string;
}

export interface FormField {
  name: string;
  label: string;
  field_type: string;
  required?: boolean;
  options?: { value: string; label: string }[];
  fk_endpoint?: string | null;
  placeholder?: string | null;
  veda_filled?: boolean;
  veda_confidence?: number | null;
  readonly?: boolean;
}

export interface FormPayload {
  record_type: string;
  record_id?: string | null;
  fields: FormField[];
  values: Record<string, unknown>;
  submit_endpoint: string;
  submit_method: 'POST' | 'PATCH' | 'PUT';
}

export interface ApprovalPayload {
  record_type: string;
  record_id: string;
  summary: Record<string, string>;
  action_options: string[];
}

export interface BlockerPayload {
  reason: string;
  resolution_options: UIAction[];
  blocked_task?: string | null;
}

export interface ConfirmPayload {
  summary: Record<string, string>;
  warning?: string | null;
  is_irreversible?: boolean;
}

export interface ProgressStep {
  label: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  detail?: string | null;
}

export interface ProgressPayload {
  steps: ProgressStep[];
  current_step: number;
  percent: number;
  task_id?: string | null;
}

export interface TextPayload {
  content: string;
  hints: string[];
}

export type UIPayload =
  | TablePayload | FormPayload | ApprovalPayload | BlockerPayload
  | ConfirmPayload | ProgressPayload | TextPayload;

export interface UIResponse {
  type: UIResponseType;
  message: string;
  payload: UIPayload | null;
  actions: UIAction[];
  context: UIContext;
  veda_confidence?: number | null;
  audit_note?: string | null;
}

export interface VEDAMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: UIResponse;
  timestamp: Date;
}

export type UserRole =
  | 'owner' | 'hr_manager' | 'finance_manager'
  | 'manager' | 'employee' | 'auditor';

export interface UserContext {
  user_id: string;
  tenant_id: string;
  role: UserRole;
  full_name: string;
  company_name: string;
}
