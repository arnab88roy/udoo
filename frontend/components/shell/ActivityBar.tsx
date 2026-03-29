'use client';

import { Settings, Home as HomeIcon } from 'lucide-react';
import { NAV_MODULES } from '@/lib/design-system';

interface ActivityBarProps {
  activeModule: string;
  onModuleChange: (mod: string) => void;
  visibleModules: string[];
}

export function ActivityBar({ activeModule, onModuleChange, visibleModules }: ActivityBarProps) {
  return (
    <div className="flex flex-col items-center py-4 gap-4 border-r border-(--border-subtle) bg-(--bg-panel) w-[60px] shrink-0 z-40">
      
      {/* Home/Dashboard */}
      <button
        onClick={() => onModuleChange('home')}
        className={`w-10 h-10 flex items-center justify-center rounded-xl transition-all duration-200 ${
          activeModule === 'home'
            ? 'text-(--veda-purple) bg-(--veda-purple-bg) shadow-sm ring-1 ring-(--veda-purple-border)'
            : 'text-(--text-muted) hover:text-(--text-primary) hover:bg-(--bg-panel-hover)'
        }`}
        title="DASHBOARD"
      >
        <HomeIcon size={20} />
      </button>

      <div className="w-8 h-px bg-(--border-subtle) opacity-50" />

      {/* Dynamic Modules */}
      {NAV_MODULES.filter(m => visibleModules.includes(m.id)).map((mod) => {
        const Icon = mod.icon;
        return (
          <button
            key={mod.id}
            onClick={() => onModuleChange(mod.id)}
            className={`w-10 h-10 flex items-center justify-center rounded-xl transition-all duration-300 ${
              activeModule === mod.id
                ? 'text-(--veda-purple) bg-(--veda-purple-bg) shadow-md ring-1 ring-(--veda-purple-border)'
                : 'text-(--text-muted) hover:text-(--text-primary) hover:bg-(--bg-panel-hover)'
            }`}
            title={mod.label.toUpperCase()}
          >
            <Icon size={20} />
          </button>
        );
      })}

      {/* Bottom Actions */}
      <div className="mt-auto flex flex-col items-center gap-4 pb-2">
         <button className="text-(--text-muted) hover:text-(--text-primary) transition-all p-2 rounded-lg hover:bg-(--bg-panel-hover)">
          <Settings size={20} />
        </button>
        <div className="w-8 h-8 rounded-full bg-linear-to-tr from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-800 flex items-center justify-center border border-(--border-subtle) cursor-pointer hover:ring-2 ring-(--veda-purple-border) transition-all">
          <span className="text-[10px] font-bold">AR</span>
        </div>
      </div>
    </div>
  );
}
