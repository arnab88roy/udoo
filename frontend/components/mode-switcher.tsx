"use client"

import * as React from "react"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { VEDAMode, VEDA_MODE_LABELS } from "@/lib/design-system"
import { Sparkles, Monitor } from "lucide-react"

interface ModeSwitcherProps {
  currentMode: VEDAMode
  onModeChange: (mode: VEDAMode) => void
}

export function ModeSwitcher({ currentMode, onModeChange }: ModeSwitcherProps) {
  return (
    <Tabs
      value={currentMode}
      onValueChange={(value) => onModeChange(value as VEDAMode)}
      className="w-auto"
    >
      <TabsList className="grid w-full grid-cols-2 h-8 p-1 bg-muted/50 rounded-lg">
        <TabsTrigger
          value="auto"
          className="text-[10px] font-bold uppercase tracking-wider gap-2 px-3 py-1 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm"
        >
          <Monitor size={12} className="opacity-70" />
          <span className="hidden sm:inline">{VEDA_MODE_LABELS["auto"]}</span>
          <span className="sm:hidden">Auto</span>
        </TabsTrigger>
        <TabsTrigger
          value="assist"
          className="text-[10px] font-bold uppercase tracking-wider gap-2 px-3 py-1 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm data-[state=active]:shadow-primary/20"
        >
          <Sparkles size={12} className="opacity-70" />
          <span className="hidden sm:inline">{VEDA_MODE_LABELS["assist"]}</span>
          <span className="sm:hidden">Assist</span>
        </TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
