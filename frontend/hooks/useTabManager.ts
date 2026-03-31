'use client';

import { useState, useEffect } from 'react';
import { UIContext } from '@/types/ui-response';

export type TabType = 'list' | 'form' | 'welcome' | 'dashboard';

export interface Tab {
  id: string;
  label: string;
  type: TabType;
  path: string;
  module: string;
  context?: UIContext;
}

const STORAGE_KEY = 'udoo_tabs_state';

interface TabsState {
  tabs: Tab[];
  activeTabId: string | null;
}

export function useTabManager() {
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const { tabs: savedTabs, activeTabId: savedActiveId } = JSON.parse(saved);
        setTabs(savedTabs || []);
        setActiveTabId(savedActiveId || null);
      } catch (e) {
        console.error('Failed to load tabs from storage', e);
      }
    }
    setIsLoaded(true);
  }, []);

  // Sync to localStorage
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ tabs, activeTabId }));
    }
  }, [tabs, activeTabId, isLoaded]);

  const addTab = (tab: Omit<Tab, 'id'>) => {
    // Check if tab with same path/id exists
    const existingIndex = tabs.findIndex(t => t.path === tab.path);
    
    if (existingIndex !== -1) {
      setActiveTabId(tabs[existingIndex].id);
      return;
    }

    const newTab: Tab = {
      ...tab,
      id: crypto.randomUUID(),
    };

    setTabs(prev => [...prev, newTab]);
    setActiveTabId(newTab.id);
  };

  const removeTab = (id: string) => {
    setTabs(prev => {
      const newTabs = prev.filter(t => t.id !== id);
      return newTabs;
    });
    // Use functional updater to avoid stale activeTabId closure
    setActiveTabId(prev => {
      if (prev !== id) return prev;
      const remaining = tabs.filter(t => t.id !== id);
      return remaining.length > 0 ? remaining[remaining.length - 1].id : null;
    });
  };

  const closeOthers = (keepId: string) => {
    setTabs(prev => prev.filter(t => t.id === keepId));
    setActiveTabId(keepId);
  };

  const closeAll = () => {
    setTabs([]);
    setActiveTabId(null);
  };

  const activeTab = tabs.find(t => t.id === activeTabId) || null;

  return {
    tabs,
    activeTab,
    activeTabId,
    addTab,
    removeTab,
    closeOthers,
    closeAll,
    setActiveTabId,
    isLoaded
  };
}
