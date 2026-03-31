import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "h-10 w-full min-w-0 rounded-xl border border-input/60 bg-background/50 px-3 py-1 text-base shadow-none transition-all outline-none placeholder:text-muted-foreground disabled:pointer-events-none disabled:opacity-50 md:text-sm",
        "focus-visible:border-primary/40 focus-visible:ring-[3px] focus-visible:ring-primary/10",
        className
      )}
      {...props}
    />
  )
}

export { Input }
