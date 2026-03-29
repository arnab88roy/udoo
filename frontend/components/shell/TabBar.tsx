'use client';

import { X, Layout, FileText, Users, DollarSign, Settings, Home as HomeIcon } from 'lucide-react';
import { Tab } from '@/hooks/useTabManager';

interface TabBarProps {
  tabs: Tab[];
  activeTabId: string | null;
  onTabClick: (id: string) => void;
  onTabClose: (id: string, e: React.MouseEvent) => void;
}

const TAB_ICONS: Record<string, React.ReactNode> = {
  home: <HomeIcon size={14} />,
  hrms: <Users size={14} />,
  payroll: <DollarSign size={14} />,
  finance: <FileText size={14} />,
  settings: <Settings size={14} />,
};

export function TabBar({ tabs, activeTabId, onTabClick, onTabClose }: TabBarProps) {
  if (tabs.length === 0) return null;

  return (
    <div className="flex h-10 bg-(--bg-panel)/30 border-b border-(--border-subtle) overflow-x-auto overflow-y-hidden no-scrollbar z-30 shrink-0">
      {tabs.map((tab) => {
        const isActive = tab.id === activeTabId;
        return (
          <div
            key={tab.id}
            onClick={() => onTabClick(tab.id)}
            className={`
              group relative flex items-center h-full min-w-[120px] max-w-[240px] px-4 gap-2 border-r border-(--border-subtle) cursor-pointer select-none transition-all duration-200
              ${isActive 
                ? 'bg-(--bg-base) text-(--text-primary) shadow-[0_-2px_0_inset_var(--veda-purple)]' 
                : 'text-(--text-secondary) hover:bg-(--bg-panel-hover)/50 hover:text-(--text-primary)'}
            `}
          >
            {/* Icon */}
            <div className={`transition-colors ${isActive ? 'text-(--veda-purple)' : 'text-(--text-muted)'}`}>
                {TAB_ICONS[tab.module] || <FileText size={14} />}
            </div>

            {/* Label */}
            <span className="flex-1 truncate text-xs font-semibold tracking-tight transition-transform">
              {tab.label}
            </span>

            {/* Close Button */}
            <button
              onClick={(e) => onTabClose(tab.id, e)}
              className={`
                p-0.5 rounded-md transition-all
                ${isActive ? 'opacity-100 hover:bg-(--bg-panel-hover)' : 'opacity-0 group-hover:opacity-100 hover:bg-(--bg-panel-hover)'}
              `}
            >
              <X size={12} className="text-(--text-muted) hover:text-(--text-primary)" />
            </button>

            {/* Active Highlight (Bottom border) */}
            {isActive && (
                 <div className="absolute bottom-0 left-0 w-full h-0.5 bg-linear-to-r from-(--veda-purple) to-blue-500 shadow-[0_0_8px_var(--veda-purple)]" />
            )}
          </div>
        );
      })}
    </div>
  );
}
