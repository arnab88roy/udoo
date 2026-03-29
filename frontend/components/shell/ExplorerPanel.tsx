'use client';

import { Search, ChevronDown, ChevronRight, File, List, FormInput, PieChart } from 'lucide-react';
import { NAV_MODULES } from '@/lib/design-system';
import { Tab } from '@/hooks/useTabManager';

interface ExplorerPanelProps {
  activeModule: string;
  onOpenTab: (tab: Omit<Tab, 'id'>) => void;
  activeTabId: string | null;
}

export function ExplorerPanel({ activeModule, onOpenTab, activeTabId }: ExplorerPanelProps) {
  const moduleConfig = NAV_MODULES.find((m) => m.id === activeModule);

  if (!moduleConfig) {
    return (
      <div className="flex flex-col h-full bg-(--bg-panel)/50 backdrop-blur-md">
        <div className="px-4 py-3 border-b border-(--border-subtle)">
          <span className="text-(--text-primary) text-[11px] font-bold uppercase tracking-widest leading-none">
            {activeModule}
          </span>
        </div>
        <div className="p-8 text-center">
          <p className="text-(--text-muted) text-xs italic">No items found for this module.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full w-full bg-(--bg-panel)/50 backdrop-blur-md overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-(--border-subtle) flex items-center justify-between">
        <span className="text-(--text-primary) text-[11px] font-bold uppercase tracking-widest leading-none">
          {moduleConfig.label}
        </span>
      </div>

      {/* Search Bar */}
      <div className="px-2 py-2">
        <div className="relative group">
          <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-(--text-muted) group-focus-within:text-(--veda-purple) transition-colors" />
          <input
            type="text"
            placeholder="Search items..."
            className="w-full bg-(--bg-panel-hover)/50 border border-transparent focus:border-(--veda-purple-border) rounded-md pl-8 pr-2 py-1.5 text-xs outline-none transition-all placeholder:text-(--text-muted)/50"
          />
        </div>
      </div>

      {/* Navigation Tree */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden py-2 custom-scrollbar">
        
        {/* Core Navigation Items */}
        <div className="px-2 space-y-0.5">
          {moduleConfig.items.map((item) => (
            <button
              key={item.href}
              onClick={() => onOpenTab({
                label: item.label,
                path: item.href,
                type: 'list', // Map href to type later
                module: activeModule
              })}
              className={`
                w-full group flex items-center gap-2 px-2 py-1.5 rounded-md transition-all text-left
                ${activeTabId && item.href.includes(activeTabId) // Simple check, refactor later
                    ? 'bg-(--veda-purple-bg) text-(--veda-purple) ring-1 ring-(--veda-purple-border)' 
                    : 'text-(--text-secondary) hover:bg-(--bg-panel-hover) hover:text-(--text-primary)'}
              `}
            >
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <div className="w-1.5 h-1.5 rounded-full bg-(--veda-purple)/40 group-hover:bg-(--veda-purple) transition-colors" />
                <span className="truncate text-[12px] font-medium leading-tight">{item.label}</span>
              </div>
            </button>
          ))}
        </div>

        {/* Categories (Masters, Transactions, Reports) — Hardcoded for now, refactor to meta-engine later */}
        <div className="mt-4 px-2">
            <div className="flex items-center gap-2 px-2 py-1 text-(--text-muted) opacity-40 uppercase tracking-tighter font-bold text-[9px]">
                <ChevronDown size={10} />
                <span>Reports</span>
            </div>
            <div className="mt-1 space-y-0.5 opacity-60">
                <button className="w-full text-left px-5 py-1.5 text-[11px] text-(--text-secondary) hover:bg-(--bg-panel-hover) hover:text-(--text-primary) rounded-md flex items-center gap-2">
                    <PieChart size={12} />
                    <span>Module Analytics</span>
                </button>
                <button className="w-full text-left px-5 py-1.5 text-[11px] text-(--text-secondary) hover:bg-(--bg-panel-hover) hover:text-(--text-primary) rounded-md flex items-center gap-2">
                    <PieChart size={12} />
                    <span>Audit Trail</span>
                </button>
            </div>
        </div>
      </div>
    </div>
  );
}
