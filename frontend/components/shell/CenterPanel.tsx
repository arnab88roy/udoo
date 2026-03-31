'use client';

import { TabBar } from './TabBar';
import { WelcomeScreen } from './WelcomeScreen';
import { Layout } from 'lucide-react';
import { useTabManager } from '@/hooks/useTabManager';

interface CenterPanelProps {
  tabManager: ReturnType<typeof useTabManager>;
}

export function CenterPanel({ tabManager }: CenterPanelProps) {
  const { tabs, activeTab, activeTabId, setActiveTabId, removeTab } = tabManager;

  const handleTabClick = (id: string) => {
    setActiveTabId(id);
  };

  const handleTabClose = (id: string) => {
    removeTab(id);
  };

  const handleCloseOthers = (id: string) => {
    tabManager.closeOthers(id);
  };

  const handleCloseAll = () => {
    tabManager.closeAll();
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-transparent">
      
      {/* 1. Tab Bar */}
      <TabBar 
        tabs={tabs} 
        activeTabId={activeTabId} 
        onTabClick={handleTabClick} 
        onTabClose={handleTabClose} 
        onCloseOthers={handleCloseOthers}
        onCloseAll={handleCloseAll}
      />

      {/* 2. Content Area — The White Sheet Starts Here */}
      <div className="flex-1 overflow-auto bg-sheet shadow-sheet rounded-2xl p-6">
        {activeTab ? (
          <div className="max-w-4xl mx-auto h-full flex flex-col items-center justify-center text-center animate-in fade-in zoom-in-95 duration-500">
             <div className="relative group mb-8">
                <div className="absolute -inset-1 bg-linear-to-tr from-primary/20 to-blue-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition duration-500" />
                <div className="relative w-20 h-20 rounded-3xl bg-white border-none flex items-center justify-center shadow-lg">
                   <Layout className="h-10 w-10 text-primary/40" />
                </div>
             </div>
             
             <h3 className="text-2xl font-extrabold tracking-tight text-foreground mb-2">
               {activeTab.label}
             </h3>
             <p className="text-sm text-muted-foreground max-w-sm mb-10 font-medium leading-relaxed">
                The interface for <span className="text-primary font-bold">{activeTab.path}</span> is currently being synthesized by the Meta-Engine.
             </p>

             <div className="w-full grid grid-cols-3 gap-6 opacity-30 pointer-events-none">
                <div className="h-32 rounded-xl bg-muted/20 border-none shadow-none" />
                <div className="h-32 rounded-xl bg-muted/20 border-none shadow-none" />
                <div className="h-32 rounded-xl bg-muted/20 border-none shadow-none" />
                <div className="col-span-3 h-64 rounded-xl bg-muted/20 border-none shadow-none" />
             </div>
          </div>
        ) : (
          <WelcomeScreen />
        )}
      </div>
    </div>
  );
}
