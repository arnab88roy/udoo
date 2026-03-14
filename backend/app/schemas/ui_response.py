from enum import Enum
from uuid import UUID
from typing import List, Optional, Union, Literal, Dict
from pydantic import BaseModel, Field, ConfigDict

# SECTION 1: UIResponseType Enum

class UIResponseType(str, Enum):
    TABLE    = "table"
    FORM     = "form"
    APPROVAL = "approval"
    BLOCKER  = "blocker"
    CONFIRM  = "confirm"
    PROGRESS = "progress"
    TEXT     = "text"

# SECTION 2: UIContext

class UIContext(BaseModel):
    """
    The active record context at the time of the VEDA request.
    Passed automatically by the frontend on every message.
    VEDA uses this to scope queries without the user specifying a subject.
    """
    open_record_type: Optional[str] = Field(
        None,
        description="Type of the record currently open in the editor. "
                    "e.g. 'employee', 'leave_application', 'salary_slip', 'invoice'. "
                    "Null if no record is open (e.g. user is on home dashboard)."
    )
    open_record_id: Optional[UUID] = Field(
        None,
        description="UUID of the specific record currently open. "
                    "Null if no record is open. "
                    "Never assume record identity when this is null — always ask."
    )
    open_module: Optional[str] = Field(
        None,
        description="The module the user is currently working in. "
                    "One of: 'hrms', 'payroll', 'finance', 'settings'. "
                    "Used by LangGraph supervisor for agent routing."
    )
    tenant_id: UUID = Field(
        ...,
        description="The tenant this request belongs to. "
                    "Always overwritten server-side from the JWT. "
                    "Client-supplied value is ignored."
    )

# SECTION 3: UIAction

class UIAction(BaseModel):
    """
    A clickable action button rendered inside a UIResponse card.
    When clicked, the frontend calls the specified FastAPI endpoint directly.
    Never embed action instructions in the message text — use UIAction objects.
    """
    action_id: str = Field(
        ...,
        description="Unique identifier for this action within the response. "
                    "e.g. 'approve', 'reject', 'confirm_submit', 'skip'."
    )
    label: str = Field(
        ...,
        description="Display text shown on the button. Keep it short. "
                    "e.g. 'Approve', 'Reject', 'Confirm & Submit', 'Skip'."
    )
    style: Literal["primary", "secondary", "danger", "ghost"] = Field(
        "secondary",
        description="Visual style of the button. "
                    "primary = blue filled (main action), "
                    "secondary = outlined (alternative), "
                    "danger = red (destructive actions like reject/cancel), "
                    "ghost = text only (dismiss/cancel)."
    )
    endpoint: str = Field(
        ...,
        description="The FastAPI endpoint path to call when this action is clicked. "
                    "Include the full path with IDs substituted. "
                    "e.g. '/api/leave-applications/uuid-here/approve'. "
                    "Empty string if this action requires no API call (e.g. dismiss)."
    )
    method: Literal["POST", "PUT", "PATCH", "DELETE"] = Field(
        "POST",
        description="HTTP method for the endpoint call."
    )
    payload: dict = Field(
        default_factory=dict,
        description="Request body to send with the endpoint call. "
                    "Empty dict if no body is required."
    )
    confirmation_required: bool = Field(
        False,
        description="If True, the frontend shows a secondary 'Are you sure?' prompt "
                    "before calling the endpoint. Use for irreversible actions."
    )
    sets_context: Optional[dict] = Field(
        None,
        description="If set, clicking this action updates the frontend's "
                    "active record context WITHOUT calling an API endpoint. "
                    "Use for navigation actions. "
                    "e.g. {'open_module': 'payroll', 'open_record_type': 'salary_slip'} "
                    "to navigate the user to the payroll module after a confirmation. "
                    "Can be combined with endpoint — context updates after the API call succeeds."
    )

# SECTION 4: FormField

class FormFieldType(str, Enum):
    TEXT      = "text"
    TEXTAREA  = "textarea"
    NUMBER    = "number"
    DATE      = "date"
    DATETIME  = "datetime"
    SELECT    = "select"
    FK_PICKER = "fk_picker"   # UUID foreign key with display name lookup
    TOGGLE    = "toggle"
    FILE      = "file"
    READONLY  = "readonly"    # computed or locked field

class FormField(BaseModel):
    """
    Definition of a single field in an inline form card.
    Used by InlineForm component to render the correct input type.
    """
    name: str = Field(
        ...,
        description="The field's key name as it appears in the Pydantic schema. "
                    "e.g. 'first_name', 'department_id', 'attendance_date'."
    )
    label: str = Field(
        ...,
        description="Human-readable label shown above the input. "
                    "e.g. 'First Name', 'Department', 'Attendance Date'."
    )
    field_type: FormFieldType = Field(
        ...,
        description="The input type to render. Determines which UI component is used."
    )
    required: bool = Field(
        False,
        description="If True, form cannot be submitted without this field."
    )
    options: Optional[List[dict]] = Field(
        None,
        description="For SELECT fields: list of {value, label} options. "
                    "e.g. [{'value': 'Present', 'label': 'Present'}, ...]"
    )
    fk_endpoint: Optional[str] = Field(
        None,
        description="For FK_PICKER fields: the GET endpoint to fetch options from. "
                    "e.g. '/api/departments/' to populate a department picker."
    )
    placeholder: Optional[str] = Field(
        None,
        description="Placeholder text shown in the input when empty."
    )
    veda_filled: bool = Field(
        False,
        description="True if VEDA populated this field's value (not the human). "
                    "The frontend renders a purple left border on veda_filled fields "
                    "to show transparent attribution. Human can override."
    )
    veda_confidence: Optional[float] = Field(
        None,
        description="VEDA's confidence in the value it filled. 0.0 to 1.0. "
                    "Only set when veda_filled=True. "
                    "Below 0.8 renders an amber warning indicator on the field."
    )
    readonly: bool = Field(
        False,
        description="If True, field is displayed but not editable. "
                    "Used for computed fields like net_pay, employee_id."
    )

# SECTION 5: ProgressStep

class ProgressStepStatus(str, Enum):
    PENDING     = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED   = "completed"
    FAILED      = "failed"
    SKIPPED     = "skipped"

class ProgressStep(BaseModel):
    """
    A single step in a PROGRESS type response.
    Rendered as a step list with status icons.
    """
    label: str = Field(
        ...,
        description="Short description of this step. "
                    "e.g. 'Fetching employees', 'Calculating PF deductions'."
    )
    status: ProgressStepStatus = Field(
        ProgressStepStatus.PENDING,
        description="Current status of this step."
    )
    detail: Optional[str] = Field(
        None,
        description="Optional detail shown below the step label. "
                    "e.g. '22 employees found', '3 anomalies detected'."
    )

# SECTION 6: Payload Types (one per UIResponseType)

class TablePayload(BaseModel):
    """Payload for TABLE type responses. Renders an inline data table."""
    columns: List[str] = Field(
        ...,
        description="Column keys to display. Order determines column order. "
                    "Must match keys in the rows dicts."
    )
    column_labels: Optional[dict] = Field(
        None,
        description="Optional display labels for columns. "
                    "e.g. {'employee_id': 'Employee ID', 'net_pay': 'Net Pay (₹)'}. "
                    "Falls back to column key if not provided."
    )
    rows: List[dict] = Field(
        ...,
        description="The data rows. Each dict must have keys matching 'columns'."
    )
    total: int = Field(
        ...,
        description="Total number of records (may exceed len(rows) if paginated)."
    )
    page: int = Field(
        1,
        description="Current page number for paginated results."
    )
    page_size: int = Field(
        25,
        description="Number of rows per page."
    )
    record_type: Optional[str] = Field(
        None,
        description="Entity type of each row. "
                    "e.g. 'employee', 'leave_application', 'salary_slip'. "
                    "Used by the frontend to make rows clickable — "
                    "clicking a row sets open_record_id in the active context. "
                    "Null if rows are not individually navigable."
    )
    row_id_field: str = Field(
        "id",
        description="The key in each row dict that contains the record UUID. "
                    "Used to set open_record_id when a row is clicked. "
                    "Default: 'id'. Override if the UUID key has a different name."
    )


class FormPayload(BaseModel):
    """Payload for FORM type responses. Renders an editable inline form."""
    record_type: str = Field(
        ...,
        description="The entity type this form represents. "
                    "e.g. 'employee', 'leave_application', 'salary_slip'."
    )
    record_id: Optional[UUID] = Field(
        None,
        description="UUID of the existing record being edited. "
                    "Null for new record creation forms."
    )
    fields: List[FormField] = Field(
        ...,
        description="Field definitions in display order."
    )
    values: dict = Field(
        default_factory=dict,
        description="Current field values keyed by field name. "
                    "Pre-populated by VEDA where possible."
    )
    submit_endpoint: str = Field(
        ...,
        description="The FastAPI endpoint to POST/PATCH when the form is saved. "
                    "e.g. '/api/employees/' for create, '/api/employees/uuid' for update."
    )
    submit_method: Literal["POST", "PATCH", "PUT"] = Field(
        "POST",
        description="HTTP method for form submission."
    )


class ApprovalPayload(BaseModel):
    """Payload for APPROVAL type responses. Renders an approval decision card."""
    record_type: str = Field(
        ...,
        description="The entity type awaiting approval. "
                    "e.g. 'leave_application', 'attendance_request', 'expense_claim'."
    )
    record_id: UUID = Field(
        ...,
        description="UUID of the record awaiting approval."
    )
    summary: dict = Field(
        ...,
        description="Key-value pairs summarising the record for the approver. "
                    "e.g. {'employee': 'Dev Patel', 'leave_type': 'Casual Leave', "
                    "'dates': 'Mar 18-20', 'balance_after': '7 days remaining'}."
    )
    action_options: List[str] = Field(
        ...,
        description="Human-readable list of available decisions. "
                    "e.g. ['Approve', 'Reject', 'Ask for reason']. "
                    "Each option corresponds to a UIAction in the parent UIResponse."
    )


class BlockerPayload(BaseModel):
    """
    Payload for BLOCKER type responses.
    VEDA has hit a situation it cannot resolve without human input.
    Renders a warning card with resolution options.
    """
    reason: str = Field(
        ...,
        description="Clear explanation of why VEDA cannot proceed. "
                    "Be specific. e.g. 'Bank account changed 3 days ago. "
                    "Policy requires 7-day wait or second-level approval.' "
                    "Not 'Something went wrong.'"
    )
    resolution_options: List[UIAction] = Field(
        ...,
        description="The available paths forward. Each is a UIAction the human can take. "
                    "Always include at least one option. "
                    "e.g. 'Request second-level approval', 'Skip this employee', 'Edit policy'."
    )
    blocked_task: Optional[str] = Field(
        None,
        description="Description of the task that was interrupted. "
                    "VEDA will resume this task after the blocker is resolved. "
                    "e.g. 'Generating March 2026 payroll for 47 employees'."
    )


class ConfirmPayload(BaseModel):
    """
    Payload for CONFIRM type responses.
    VEDA is about to execute an action with significant consequences.
    Requires explicit human confirmation before proceeding.
    Always shown before bulk operations, submissions, or deletions.
    """
    summary: dict = Field(
        ...,
        description="Key-value summary of what VEDA is about to do. "
                    "e.g. {'action': 'Submit payroll', 'month': 'March 2026', "
                    "'employees': 47, 'total_net_pay': '₹32,45,000'}."
    )
    warning: Optional[str] = Field(
        None,
        description="Optional warning shown in amber. "
                    "e.g. 'Submitted slips cannot be edited. They can only be cancelled.' "
                    "Use for irreversible or high-impact actions."
    )
    is_irreversible: bool = Field(
        False,
        description="If True, renders a red 'This cannot be undone' banner. "
                    "Reserve for truly irreversible operations like permanent deletion."
    )


class ProgressPayload(BaseModel):
    """
    Payload for PROGRESS type responses.
    Renders a step-by-step progress card for long-running background operations.
    Used for bulk payroll generation, bulk attendance import, etc.
    """
    steps: List[ProgressStep] = Field(
        ...,
        description="The ordered list of steps in this operation. "
                    "Each step updates as the background task progresses."
    )
    current_step: int = Field(
        0,
        description="Zero-based index of the currently executing step."
    )
    percent: int = Field(
        0,
        ge=0,
        le=100,
        description="Overall completion percentage. 0-100."
    )
    task_id: Optional[str] = Field(
        None,
        description="Optional background task ID for polling status updates. "
                    "Frontend uses this to poll GET /api/tasks/{task_id}/status."
    )


class TextPayload(BaseModel):
    """
    Payload for TEXT type responses.
    Used ONLY for greetings, acknowledgements, and simple answers
    that require no data interaction.
    Never use TEXT for responses that involve database records.
    """
    content: str = Field(
        ...,
        description="The full text content of the response. "
                    "Can include markdown for formatting."
    )
    hints: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up actions shown as clickable chips below the message. "
                    "e.g. ['Show pending leaves', 'Run payroll for this month', 'Add a new employee']. "
                    "Max 4 hints. Keep each under 40 characters."
    )

# SECTION 7: VEDARequest

class VEDARequest(BaseModel):
    """
    The request body sent by the frontend to POST /api/veda/chat.
    Contains the user's message, active record context, and conversation history.
    """
    message: str = Field(
        ...,
        description="The user's natural language input to VEDA."
    )
    context: UIContext = Field(
        ...,
        description="The active record context at the time of sending. "
                    "Passed automatically by the frontend. "
                    "tenant_id is overwritten server-side from JWT — "
                    "client-supplied tenant_id is ignored."
    )
    conversation_history: List[dict] = Field(
        default_factory=list,
        max_length=10,
        description="Last 10 messages for conversational continuity. "
                    "Enforced server-side — anything beyond 10 is truncated. "
                    "Each dict: {'role': 'user'|'assistant', 'content': str}. "
                    "Do not include the current message in history."
    )

# SECTION 8: UIResponse (the root schema — this is what every VEDA call returns)

class UIResponse(BaseModel):
    """
    The root response object returned by every VEDA API call.
    Every response MUST be one of the 7 typed variants.
    The frontend uses 'type' to look up the correct React component
    in the card registry and render it inline in the chat.

    RULES (from veda-ui-response SKILL):
    1. Never return plain text for actions that affect the database.
    2. Type selection: SEE data=TABLE, VIEW/EDIT record=FORM,
       approve/reject=APPROVAL, blocked=BLOCKER,
       irreversible action=CONFIRM, long task=PROGRESS,
       greeting/acknowledgement=TEXT only.
    3. Every actionable response must include UIAction objects.
    4. Every data-modifying response must include an audit_note.
    5. Include veda_confidence when inferring (not reading) values.
    """
    type: UIResponseType = Field(
        ...,
        description="The response type. Determines which React card component renders."
    )
    message: str = Field(
        ...,
        description="VEDA's spoken response. Always present. "
                    "This is the conversational text shown above the card. "
                    "e.g. 'Here are the active employees:' or "
                    "'I cannot process this payslip for the following reason:'."
    )
    payload: Optional[Union[
        TablePayload,
        FormPayload,
        ApprovalPayload,
        BlockerPayload,
        ConfirmPayload,
        ProgressPayload,
        TextPayload
    ]] = Field(
        None,
        description="The typed payload for this response. "
                    "Must match the type field. "
                    "Null only for TEXT type with no hints."
    )
    actions: List[UIAction] = Field(
        default_factory=list,
        description="Action buttons rendered at the bottom of the card. "
                    "Every APPROVAL must have at least Approve + Reject actions. "
                    "Every CONFIRM must have at least Confirm + Cancel actions. "
                    "TABLE and FORM may have optional actions like Export or Save."
    )
    context: UIContext = Field(
        ...,
        description="The active record context at the time VEDA generated this response. "
                    "Echoed back so the frontend can verify context alignment."
    )
    veda_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="VEDA's overall confidence in this response. 0.0 to 1.0. "
                    "Set when VEDA inferred something rather than reading it directly. "
                    "Below 0.7 renders an amber 'Review carefully' indicator on the card."
    )
    audit_note: Optional[str] = Field(
        None,
        description="Written to the audit log with VEDA attribution and timestamp. "
                    "Required for any response that modifies database state. "
                    "e.g. 'Leave approved by VEDA on behalf of manager Arnab.'"
    )

# SECTION 9: CONVENIENCE FACTORY FUNCTIONS

def make_text_response(
    message: str,
    context: UIContext,
    hints: List[str] = None
) -> UIResponse:
    """Quick constructor for TEXT type responses."""
    return UIResponse(
        type=UIResponseType.TEXT,
        message=message,
        payload=TextPayload(content=message, hints=hints or []),
        actions=[],
        context=context
    )

def make_table_response(
    message: str,
    context: UIContext,
    columns: List[str],
    rows: List[dict],
    total: int,
    actions: List[UIAction] = None,
    column_labels: dict = None,
    record_type: str = None,
    row_id_field: str = "id"
) -> UIResponse:
    """Quick constructor for TABLE type responses."""
    return UIResponse(
        type=UIResponseType.TABLE,
        message=message,
        payload=TablePayload(
            columns=columns,
            column_labels=column_labels,
            rows=rows,
            total=total,
            record_type=record_type,
            row_id_field=row_id_field
        ),
        actions=actions or [],
        context=context
    )

def make_blocker_response(
    reason: str,
    resolution_options: List[UIAction],
    context: UIContext,
    blocked_task: str = None
) -> UIResponse:
    """Quick constructor for BLOCKER type responses."""
    return UIResponse(
        type=UIResponseType.BLOCKER,
        message="I need your input before I can continue.",
        payload=BlockerPayload(
            reason=reason,
            resolution_options=resolution_options,
            blocked_task=blocked_task
        ),
        actions=[],
        context=context
    )

def make_confirm_response(
    message: str,
    summary: dict,
    confirm_action: UIAction,
    context: UIContext,
    warning: str = None,
    is_irreversible: bool = False
) -> UIResponse:
    """Quick constructor for CONFIRM type responses."""
    cancel_action = UIAction(
        action_id="cancel",
        label="Cancel",
        style="ghost",
        endpoint="",
        method="POST",
        payload={},
        confirmation_required=False
    )
    return UIResponse(
        type=UIResponseType.CONFIRM,
        message=message,
        payload=ConfirmPayload(
            summary=summary,
            warning=warning,
            is_irreversible=is_irreversible
        ),
        actions=[confirm_action, cancel_action],
        context=context
    )

def make_approval_response(
    message: str,
    record_type: str,
    record_id: UUID,
    summary: dict,
    approve_endpoint: str,
    reject_endpoint: str,
    context: UIContext,
    action_options: List[str] = None,
    audit_note: str = None,
) -> UIResponse:
    """
    Quick constructor for APPROVAL type responses.
    Used for leave approvals, attendance request approvals,
    expense claim approvals, and any other HITL decision point.
    Always includes Approve (primary) and Reject (danger) actions.
    """
    return UIResponse(
        type=UIResponseType.APPROVAL,
        message=message,
        payload=ApprovalPayload(
            record_type=record_type,
            record_id=record_id,
            summary=summary,
            action_options=action_options or ["Approve", "Reject"],
        ),
        actions=[
            UIAction(
                action_id="approve",
                label="Approve",
                style="primary",
                endpoint=approve_endpoint,
                method="POST",
                payload={},
                confirmation_required=False,
            ),
            UIAction(
                action_id="reject",
                label="Reject",
                style="danger",
                endpoint=reject_endpoint,
                method="POST",
                payload={},
                confirmation_required=False,
            ),
        ],
        context=context,
        audit_note=audit_note or f"Approval decision requested for {record_type} {record_id}.",
    )

def make_progress_response(
    message: str,
    steps: List["ProgressStep"],
    context: UIContext,
    current_step: int = 0,
    percent: int = 0,
    task_id: str = None,
) -> UIResponse:
    """
    Quick constructor for PROGRESS type responses.
    Used for bulk payroll generation, attendance import,
    and any long-running background operation.
    The frontend polls task_id for updates if provided.
    """
    return UIResponse(
        type=UIResponseType.PROGRESS,
        message=message,
        payload=ProgressPayload(
            steps=steps,
            current_step=current_step,
            percent=percent,
            task_id=task_id,
        ),
        actions=[],
        context=context,
    )

def make_form_response(
    message: str,
    record_type: str,
    fields: List["FormField"],
    submit_endpoint: str,
    context: UIContext,
    record_id: UUID = None,
    values: dict = None,
    submit_method: str = "POST",
    audit_note: str = None,
) -> UIResponse:
    """
    Quick constructor for FORM type responses.
    Used for inline record creation and editing.
    Pre-populate values dict with VEDA-inferred data
    and set veda_filled=True on the corresponding FormField
    to trigger the purple attribution indicator in the frontend.
    """
    return UIResponse(
        type=UIResponseType.FORM,
        message=message,
        payload=FormPayload(
            record_type=record_type,
            record_id=record_id,
            fields=fields,
            values=values or {},
            submit_endpoint=submit_endpoint,
            submit_method=submit_method,
        ),
        actions=[
            UIAction(
                action_id="save",
                label="Save",
                style="primary",
                endpoint=submit_endpoint,
                method=submit_method,
                payload={},
                confirmation_required=False,
            ),
            UIAction(
                action_id="cancel",
                label="Cancel",
                style="ghost",
                endpoint="",
                method="POST",
                payload={},
                confirmation_required=False,
            ),
        ],
        context=context,
        audit_note=audit_note,
    )
