'use client';

import { TabBar } from './TabBar';
import { WelcomeScreen } from './WelcomeScreen';
import { useTabManager } from '@/hooks/useTabManager';

interface CenterPanelProps {
  tabManager: ReturnType<typeof useTabManager>;
}

export function CenterPanel({ tabManager }: CenterPanelProps) {
  const { tabs, activeTab, activeTabId, setActiveTabId, removeTab } = tabManager;

  const handleTabClick = (id: string) => {
    setActiveTabId(id);
  };

  const handleTabClose = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    removeTab(id);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-(--bg-base)">
      
      {/* 1. Tab Bar */}
      <TabBar 
        tabs={tabs} 
        activeTabId={activeTabId} 
        onTabClick={handleTabClick} 
        onTabClose={handleTabClose} 
      />

      {/* 2. Content Area */}
      <div className="flex-1 overflow-auto bg-linear-to-b from-(--bg-base) to-(--bg-panel)/20 p-6">
        {activeTab ? (
          <div className="max-w-7xl mx-auto h-full flex flex-col items-center justify-center text-center animate-in fade-in zoom-in-95 duration-500">
             {/* Stub for dynamic ERP items (Employees, Leave, etc.) */}
             <div className="w-16 h-16 rounded-3xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-6 shadow-inner">
                <div className="w-8 h-8 rounded bg-slate-200 dark:bg-slate-700 animate-pulse" />
             </div>
             <h3 className="text-xl font-black text-(--text-primary)">{activeTab.label}</h3>
             <p className="text-sm text-(--text-secondary) max-w-sm mt-2 font-medium">
                The content for <span className="text-(--veda-purple) uppercase font-bold">{activeTab.path}</span> will render here using the Meta-Engine.
             </p>
             <div className="mt-8 grid grid-cols-2 gap-4 w-full max-w-2xl opacity-40 grayscale">
                <div className="h-40 rounded-2xl border border-dashed border-(--border-subtle) bg-(--bg-panel)/50" />
                <div className="h-40 rounded-2xl border border-dashed border-(--border-subtle) bg-(--bg-panel)/50" />
                <div className="h-40 rounded-2xl border border-dashed border-(--border-subtle) bg-(--bg-panel)/50 col-span-2" />
             </div>
          </div>
        ) : (
          <WelcomeScreen />
        )}
      </div>
    </div>
  );
}
