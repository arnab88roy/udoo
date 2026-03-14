# SKILL: Frontend Card Component Registry

## The Registry Pattern
The frontend maintains a component registry keyed to UIResponse types.
When a UIResponse arrives from the API, the renderer looks up the type
and mounts the corresponding React component.

```typescript
import { UIResponseType, UIResponse } from "@/types/ui-response"
import { InlineTable } from "@/components/cards/InlineTable"
import { InlineForm } from "@/components/cards/InlineForm"
import { ApprovalCard } from "@/components/cards/ApprovalCard"
import { BlockerCard } from "@/components/cards/BlockerCard"
import { ConfirmCard } from "@/components/cards/ConfirmCard"
import { ProgressCard } from "@/components/cards/ProgressCard"
import { TextMessage } from "@/components/cards/TextMessage"

const CARD_REGISTRY: Record<UIResponseType, React.ComponentType<any>> = {
  table:    InlineTable,
  form:     InlineForm,
  approval: ApprovalCard,
  blocker:  BlockerCard,
  confirm:  ConfirmCard,
  progress: ProgressCard,
  text:     TextMessage,
}

function VEDAMessageRenderer({ response }: { response: UIResponse }) {
  const Component = CARD_REGISTRY[response.type]
  return (
    <div className="veda-message">
      <TextMessage message={response.message} />
      {Component && response.type !== "text" && (
        <Component payload={response.payload} actions={response.actions} />
      )}
    </div>
  )
}
```

---

## VEDA Diff Attribution
Fields in `InlineForm` that were filled by VEDA (not the human) must:

- Have a purple left border: `border-l-2 border-[#7C3AED]`
- Show a "VEDA" attribution badge on hover (tooltip or inline chip)
- Be individually editable — clicking removes the purple tint and marks field as human-edited
- Support "Accept all" / "Reject all" controls at the form level

CSS custom property:
```css
--color-veda-fill: #7C3AED;
--color-veda-fill-bg: #F5F3FF;
```

Field attribution tracking:
```typescript
type FieldAttribution = "veda" | "human"

interface FormFieldState {
  value: any
  attribution: FieldAttribution
  confidence?: number  // 0.0-1.0, from UIResponse.veda_confidence
}
```

---

## Card Interaction Rules

1. **Action buttons** in cards call FastAPI endpoints directly (using the `endpoint` + `method` from UIAction)
2. **On success:** card updates in place — no page reload, no navigation
3. **On error:** card shows inline error state with the error message
4. **After CONFIRM:** card becomes read-only with a green completion stamp and timestamp
5. **After BLOCKER resolved:** VEDA automatically sends the next message to continue the interrupted task
6. **After APPROVAL:** card collapses to a summary state ("Approved by [user] at [time]")

---

## Never Do This
- Never navigate to a new page as a result of a card action
- Never show a modal for approvals — use inline cards in the conversation
- Never return to home after an action — conversation continues in place
- Never reload the page after a submit — use optimistic UI updates
- Never show raw JSON in the chat — always render through the component registry

---

## IDE Shell Layout Rules
The 4-panel layout is non-negotiable:

```
Activity Bar (48px) | Left Panel (240px) | Center Panel (flex:1) | Right Panel (300px)
```

- **Center panel** is the ONLY place where VEDA messages render
- **Left panel** shows: module tree, record navigator, pending badge counts
- **Right panel** shows: inspector for the open record, audit trail, field history
- **Activity bar** shows: module icons with live badge counts (pending approvals, etc.)

Card components render ONLY in the center panel. Never in left or right panels.

---

## Streaming Behaviour
Using Vercel AI SDK (`useChat` hook):

```typescript
const { messages, input, handleSubmit } = useChat({
  api: "/api/veda/chat",
  body: { context: activeContext },  // injected automatically
})
```

- As tokens stream in, parse partial JSON progressively
- Show a typing indicator until the `type` field is resolved
- Once `type` is known, mount the correct skeleton component
- Hydrate the component as the `payload` object completes
- `actions` render last (after payload is fully received)
