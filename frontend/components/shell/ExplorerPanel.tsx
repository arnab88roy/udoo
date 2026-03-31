'use client';

import { useState } from 'react';
import { Search, ChevronRight, Briefcase, CreditCard, Landmark, Settings, PanelLeftClose } from 'lucide-react';
import { Tab } from '@/hooks/useTabManager';
import { Input } from '@/components/ui/input';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface ExplorerPanelProps {
  activeModule: string;
  onOpenTab: (tab: Omit<Tab, 'id'>) => void;
  activeTab: Tab | null;
  onToggle?: () => void;
}

const EXPLORER_SECTIONS = [
  {
    id: 'hrms',
    label: 'HRMS',
    icon: Briefcase,
    items: [
      { label: 'Employee', href: '/hrms/employee', type: 'list' },
      { label: 'Department', href: '/hrms/department', type: 'list' },
      { label: 'Designation', href: '/hrms/designation', type: 'list' },
      { label: 'Leave Application', href: '/hrms/leave-application', type: 'list' },
      { label: 'Attendance', href: '/hrms/attendance', type: 'list' },
    ]
  },
  {
    id: 'payroll',
    label: 'PAYROLL',
    icon: CreditCard,
    items: [
      { label: 'Salary Slip', href: '/payroll/salary-slip', type: 'list' },
      { label: 'Salary Structure', href: '/payroll/salary-structure', type: 'list' },
      { label: 'Payroll Entry', href: '/payroll/payroll-entry', type: 'list' },
    ]
  },
  {
    id: 'finance',
    label: 'FINANCE',
    icon: Landmark,
    items: [
      { label: 'Sales Invoice', href: '/finance/sales-invoice', type: 'list' },
      { label: 'Purchase Invoice', href: '/finance/purchase-invoice', type: 'list' },
      { label: 'Journal Entry', href: '/finance/journal-entry', type: 'list' },
      { label: 'Chart of Accounts', href: '/finance/chart-of-accounts', type: 'list' },
    ]
  },
  {
    id: 'settings',
    label: 'SETTINGS',
    icon: Settings,
    items: [
      { label: 'Company', href: '/settings/company', type: 'list' },
      { label: 'Branch', href: '/settings/branch', type: 'list' },
      { label: 'User', href: '/settings/user', type: 'list' },
      { label: 'Role', href: '/settings/role', type: 'list' },
    ]
  }
];

export function ExplorerPanel({ activeModule, onOpenTab, activeTab, onToggle }: ExplorerPanelProps) {
  const [openSections, setOpenSections] = useState<string[]>(['hrms']);
  const [searchQuery, setSearchQuery] = useState('');

  const toggleSection = (id: string) => {
    setOpenSections(prev => 
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  const filteredSections = EXPLORER_SECTIONS.map(section => ({
    ...section,
    items: section.items.filter(item => 
      item.label.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(section => section.items.length > 0);

  return (
    <div className="flex flex-col h-full w-full overflow-hidden bg-transparent">
      {/* Header */}
      <div className="px-4 py-3 flex items-center justify-between border-b border-white/10">
        <span className="text-[10px] font-bold uppercase tracking-widest leading-none text-glass-fg-secondary">
          Explorer
        </span>
        {onToggle && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="h-6 w-6 text-glass-fg-inactive hover:text-glass-fg-primary hover:bg-white/10"
          >
            <PanelLeftClose className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>

      {/* Search Bar */}
      <div className="px-3 py-3 border-b border-white/10">
        <div className="relative group">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-glass-fg-muted group-focus-within:text-glass-fg-primary transition-colors" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search modules..."
            className="h-8 pl-8 text-xs border-transparent focus-visible:ring-1 bg-white/5 text-glass-fg-primary placeholder:text-glass-fg-muted"
          />
        </div>
      </div>

      {/* Navigation Volume */}
      <ScrollArea className="flex-1">
        <div className="py-2 flex flex-col gap-1">
          {filteredSections.map((section) => {
            const Icon = section.icon;
            const isOpen = openSections.includes(section.id);
            
            return (
              <Collapsible
                key={section.id}
                open={isOpen}
                onOpenChange={() => toggleSection(section.id)}
                className="group"
              >
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-between h-8 px-2 font-semibold text-[11px] hover:bg-transparent text-white/60 hover:text-white"
                  >
                    <div className="flex items-center gap-2">
                       <ChevronRight className={cn(
                        "h-3 w-3 transition-transform duration-200",
                        isOpen ? "text-glass-fg-primary" : "text-glass-fg-inactive",
                        isOpen && "rotate-90"
                      )} />
                      <Icon className="h-3 w-3 text-glass-fg-inactive" />
                      <span className="uppercase tracking-tight text-glass-fg-secondary font-bold">{section.label}</span>
                    </div>
                    <Badge variant="outline" className="h-4 px-1 text-[9px] min-w-4 justify-center text-glass-fg-muted border-white/20">
                      {section.items.length}
                    </Badge>
                  </Button>
                </CollapsibleTrigger>
                
                <CollapsibleContent className="px-2 pb-1 space-y-0.5 animate-in slide-in-from-left-1 duration-200">
                  {section.items.map((item) => (
                    <Button
                      key={item.href}
                      variant="ghost"
                      size="sm"
                      onClick={() => onOpenTab({
                        label: item.label,
                        path: item.href,
                        type: 'list',
                        module: section.id
                      })}
                      className={cn(
                        "w-full justify-start h-8 pl-6 pr-2 text-[11px] font-normal transition-all rounded-xl",
                        activeTab?.path === item.href
                          ? "bg-white/10 text-glass-fg-primary shadow-xs font-semibold"
                          : "text-glass-fg-secondary hover:text-glass-fg-primary hover:bg-white/5"
                      )}
                    >
                      <span className="truncate">{item.label}</span>
                    </Button>
                  ))}
                </CollapsibleContent>
              </Collapsible>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}
