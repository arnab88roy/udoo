"use client";

import { Search, Bell } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";

export function TopBar({ 
  vedaOpen, 
  onVedaToggle 
}: { 
  vedaOpen: boolean; 
  onVedaToggle: () => void 
}) {
  return (
    <header className="sticky top-0 z-50 flex h-12 w-full items-center justify-between border-b border-border bg-white px-4">
      {/* Left section */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1 select-none">
          <span className="text-lg font-bold text-[var(--color-accent-primary)]">U</span>
          <span className="text-sm font-semibold text-[var(--color-text-primary)]">udoo</span>
        </div>
        <Separator orientation="vertical" className="h-4" />
        <div className="text-[13px] text-[var(--color-text-secondary)]">HRMS / Employees</div>
      </div>

      {/* Center section: Global Search */}
      <div className="relative w-[360px]">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
        <Input 
          className="h-8 rounded-full border-border bg-[var(--color-bg-sidebar)] pl-10 pr-12 text-sm placeholder:text-[var(--color-text-tertiary)] focus-visible:ring-0"
          placeholder="Search employees, slips, leaves..."
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] text-[var(--color-text-tertiary)] font-medium">
          ⌘K
        </div>
      </div>

      {/* Right section */}
      <div className="flex items-center gap-4">
        <button 
          onClick={onVedaToggle}
          className="flex items-center gap-2 hover:opacity-80 transition-opacity"
        >
          <div className={`h-2 w-2 rounded-full ${vedaOpen ? 'bg-[var(--color-accent-veda)] shadow-[0_0_8px_var(--color-accent-veda)]' : 'bg-[var(--color-text-tertiary)]'}`} />
          <span className={`text-[13px] font-medium ${vedaOpen ? 'text-[var(--color-accent-veda)]' : 'text-[var(--color-text-tertiary)]'}`}>VEDA</span>
        </button>

        <Bell className="h-4 w-4 text-[var(--color-text-secondary)] cursor-pointer hover:text-[var(--color-text-primary)]" />
        
        <div className="flex items-center gap-3">
          <span className="text-[13px] text-[var(--color-text-secondary)] font-medium">Acme Corp</span>
          <Avatar className="h-7 w-7 border">
            <AvatarImage src="" />
            <AvatarFallback className="bg-gradient-to-br from-[#1A73E8] to-[#34A853] text-[11px] text-white font-medium">A</AvatarFallback>
          </Avatar>
        </div>
      </div>
    </header>
  );
}
