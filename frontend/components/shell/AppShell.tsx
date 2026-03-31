'use client';

import { useState, useEffect } from 'react';
import { ActivityBar } from './ActivityBar';
import { ExplorerPanel } from './ExplorerPanel';
import { CenterPanel } from './CenterPanel';
import { VEDAPanel } from './VEDAPanel';
import { useTabManager } from '@/hooks/useTabManager';
import { useResizablePanel } from '@/hooks/useResizablePanel';
import { UIContext } from '@/types/ui-response';
import { buildNullContext } from '@/lib/veda-client';
import { UserRole } from '@/types/ui-response';
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';
import { VEDAMode } from '@/types/shell';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';


// ── Mock user (replace with JWT context in Task 4.3) ──────────────────────
const MOCK_USER = {
  role: 'owner' as UserRole,
  full_name: 'Arnab Roy',
  company_name: 'Udoo Demo Co.',
};

// ── RBAC: which modules each role can see ─────────────────────────────────
const MODULE_ACCESS: Record<UserRole, string[]> = {
  owner: ['home', 'hrms', 'payroll', 'finance', 'settings'],
  hr_manager: ['home', 'hrms', 'payroll'],
  finance_manager: ['home', 'finance'],
  manager: ['home', 'hrms'],
  employee: ['home', 'hrms'],
  auditor: ['home', 'hrms', 'payroll', 'finance'],
};

export function AppShell() {
  const [activeModule, setActiveModule] = useState('hrms');
  const [vedaMode, setVEDAMode] = useState<VEDAMode>('auto');
  const [activeContext, setActiveContext] = useState<UIContext>(buildNullContext());

  const visibleModules = MODULE_ACCESS[MOCK_USER.role];
  const tabManager = useTabManager();

  const explorerPanel = useResizablePanel({
    defaultWidth: 260,
    minWidth: 180,
    maxWidth: 400,
    storageKey: 'udoo_explorer',
    side: 'left',
  });

  const vedaPanel = useResizablePanel({
    defaultWidth: 340,
    minWidth: 280,
    maxWidth: 500,
    storageKey: 'udoo_veda',
    side: 'right',
  });

  // Sync activeContext with active tab
  useEffect(() => {
    if (tabManager.activeTab?.context) {
      setActiveContext(tabManager.activeTab.context);
    }
  }, [tabManager.activeTabId, tabManager.activeTab]);

  // Ctrl+\ toggles VEDA panel
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === '\\') {
        e.preventDefault();
        vedaPanel.toggle();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [vedaPanel.toggle]);

  // Module click: toggle explorer if same module, else switch + open
  const handleModuleChange = (module: string) => {
    if (module === activeModule) {
      explorerPanel.toggle();
    } else {
      setActiveModule(module);
      if (!explorerPanel.isOpen) explorerPanel.setIsOpen(true);
    }
  };

  const openRecordTab = (type: string, id: string) => {
    tabManager.addTab({
      label: `${type} ${id.slice(0, 8)}`,
      path: `/${activeModule}/${type.toLowerCase()}/${id}`,
      type: 'form',
      module: activeModule,
      context: {
        open_record_type: type,
        open_record_id: id,
        open_module: activeModule,
        tenant_id: activeContext.tenant_id
      }
    });
  };

  return (
    <TooltipProvider delayDuration={0}>
      <div className="flex h-screen w-screen overflow-hidden p-1 font-sans select-none antialiased">
        
        {/* THE UNIFIED GLASS CONTAINER */}
        <div className="flex-1 flex overflow-hidden rounded-2xl bg-glass border border-glass-border backdrop-blur-2xl shadow-2xl gap-1">



        {/* SIDEBAR — Transparent Floating Content */}
        <div className="flex shrink-0 bg-transparent border-none overflow-hidden transition-[width] duration-300"
          style={{
            width: explorerPanel.isOpen
              ? 48 + explorerPanel.width 
              : 48                       
          }}
        >
          <ActivityBar
            activeModule={activeModule}
            onModuleChange={handleModuleChange}
            visibleModules={visibleModules}
            vedaMode={vedaMode}
            onVEDAModeChange={setVEDAMode}
            isVEDAOpen={vedaPanel.isOpen}
            onToggleVEDA={vedaPanel.toggle}
          />
          {explorerPanel.isOpen && (
            <div className="flex-1 overflow-hidden" style={{ width: explorerPanel.width }}>
              <ExplorerPanel
                activeModule={activeModule}
                onOpenTab={tabManager.addTab}
                activeTab={tabManager.activeTab}
                onToggle={explorerPanel.toggle}
              />
            </div>
          )}
        </div>

        {/* Resize handle — Thin marker */}
        {explorerPanel.isOpen && (
          <div
            className="w-1 shrink-0 cursor-col-resize hover:bg-white/20 active:bg-white/40 rounded-full transition-colors z-20 my-4"
            onMouseDown={explorerPanel.onMouseDown}
          />
        )}


        {/* 3. Center Panel — Transparent wrapper for floating tabs */}
 
        {/* 3. WORKSPACE WRAPPER — Consolidates Center & VEDA with p-1 */}
        <div className="flex-1 flex min-w-0 p-1 gap-1 overflow-hidden">
          <main className="flex-1 flex flex-col min-w-0 bg-transparent overflow-hidden border-none text-foreground">
          <CenterPanel tabManager={tabManager} />
        </main>

        {/* VEDA resize handle — Thin marker */}
        <div
          className={cn(
            "w-1 shrink-0 cursor-col-resize hover:bg-white/20 active:bg-white/40 rounded-full transition-colors z-20 my-4",
            !vedaPanel.isOpen && "hidden"
          )}
          onMouseDown={vedaPanel.onMouseDown}
        />



        {/* 4. VEDA Panel — Collapsible Rail & Floating White Sheet */}
        <aside
          className="flex shrink-0 bg-transparent border-none overflow-hidden transition-[width] duration-300"
          style={{ width: vedaPanel.isOpen ? vedaPanel.width : 0 }}
        >
          {/* Assistant Side Sheet — Positioned between Center and Rail */}
          <div className="flex-1 overflow-hidden" style={{ width: vedaPanel.width }}>
            <VEDAPanel
              activeContext={activeContext}
              setActiveContext={setActiveContext}
              onRowClick={openRecordTab}
              userRole={MOCK_USER.role}
              userName={MOCK_USER.full_name}
              vedaMode={vedaMode}
              onVEDAModeChange={setVEDAMode}
              isVEDAOpen={vedaPanel.isOpen}
              onToggleVEDA={vedaPanel.toggle}
            />
          </div>


        </aside>
        </div>



        {/* Collapsed VEDA trigger — COMMENTED OUT for symmetry 
        {!vedaPanel.isOpen && (
          <button
            onClick={vedaPanel.toggle}
            className="absolute right-6 bottom-6 w-12 h-12 rounded-full bg-primary text-primary-foreground shadow-lg flex items-center justify-center hover:scale-110 transition-transform z-50 animate-in fade-in zoom-in duration-200"
          >
            <span className="text-xl font-bold">V</span>
          </button>
        )}
        */}
        </div> {/* End of Glass Container */}
      </div>
    </TooltipProvider>
  );
}
