'use client';

import { useState, useEffect } from 'react';
import { ActivityBar } from './ActivityBar';
import { ExplorerPanel } from './ExplorerPanel';
import { CenterPanel } from './CenterPanel';
import { VEDAPanel } from './VEDAPanel';
import { useTabManager } from '@/hooks/useTabManager';
import { UIContext } from '@/types/ui-response';
import { buildNullContext } from '@/lib/veda-client';
import { UserRole } from '@/types/ui-response';
import { VEDAMode } from '@/lib/design-system';

// ── Constants ─────────────────────────────────────────────────────────────
const EXPLORER_WIDTH = 260;
const VEDA_PANEL_WIDTH = 340;

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
  const [vedaMode, setVEDAMode] = useState<VEDAMode>('veda-auto');
  const [activeContext, setActiveContext] = useState<UIContext>(buildNullContext());
  const [isVedaCollapsed, setIsVedaCollapsed] = useState(false);
  
  const visibleModules = MODULE_ACCESS[MOCK_USER.role];
  const tabManager = useTabManager();

  // Sync activeContext with active tab
  useEffect(() => {
    if (tabManager.activeTab?.context) {
      setActiveContext(tabManager.activeTab.context);
    }
  }, [tabManager.activeTabId]);

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
    <div className="flex h-screen w-screen overflow-hidden bg-(--bg-base) text-(--text-primary) font-sans select-none">
      
      {/* 1. Activity Bar (Fixed Left) */}
      <ActivityBar 
        activeModule={activeModule} 
        onModuleChange={setActiveModule} 
        visibleModules={visibleModules}
      />

      {/* 2. Explorer Panel (Fixed Width) */}
      <div className="flex shrink-0 border-r border-(--border-subtle)" style={{ width: EXPLORER_WIDTH }}>
        <ExplorerPanel 
          activeModule={activeModule} 
          onOpenTab={tabManager.addTab} 
          activeTabId={tabManager.activeTabId}
        />
      </div>

      {/* 3. Center Panel (Content Stage) */}
      <div className="flex-1 flex flex-col min-w-0 bg-(--bg-base) border-r border-(--border-subtle)">
        <CenterPanel tabManager={tabManager} />
      </div>

      {/* 4. VEDA Panel (Fixed Width) */}
      {!isVedaCollapsed && (
        <div className="flex shrink-0" style={{ width: VEDA_PANEL_WIDTH }}>
          <VEDAPanel 
            activeContext={activeContext}
            setActiveContext={setActiveContext}
            onRowClick={openRecordTab}
            userRole={MOCK_USER.role}
            userName={MOCK_USER.full_name}
            vedaMode={vedaMode}
            onVEDAModeChange={setVEDAMode}
            onCollapse={() => setIsVedaCollapsed(true)} 
          />
        </div>
      )}

      {/* Collapsed VEDA Trigger */}
      {isVedaCollapsed && (
        <button 
          onClick={() => setIsVedaCollapsed(false)}
          className="absolute right-4 bottom-4 w-12 h-12 rounded-full bg-(--veda-purple) text-white shadow-xl flex items-center justify-center hover:scale-110 transition-transform z-50"
        >
          <span className="text-xl font-bold">V</span>
        </button>
      )}
    </div>
  );
}
