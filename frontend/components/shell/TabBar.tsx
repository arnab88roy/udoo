import { X, Layout, FileText, Users, DollarSign, Settings, Home as HomeIcon } from 'lucide-react';
import { Tab } from '@/hooks/useTabManager';
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface TabBarProps {
  tabs: Tab[];
  activeTabId: string | null;
  onTabClick: (id: string) => void;
  onTabClose: (id: string) => void;
  onCloseOthers: (id: string) => void;
  onCloseAll: () => void;
}

const TAB_ICONS: Record<string, React.ReactNode> = {
  home: <HomeIcon className="h-3.5 w-3.5" />,
  hrms: <Users className="h-3.5 w-3.5" />,
  payroll: <DollarSign className="h-3.5 w-3.5" />,
  finance: <FileText className="h-3.5 w-3.5" />,
  settings: <Settings className="h-3.5 w-3.5" />,
};

export function TabBar({ 
  tabs, 
  activeTabId, 
  onTabClick, 
  onTabClose,
  onCloseOthers,
  onCloseAll
}: TabBarProps) {
  if (tabs.length === 0) return null;

  return (
    <div className="flex items-center h-12 bg-transparent px-4 overflow-hidden z-30 shrink-0">
      <ScrollArea className="flex-1 h-full w-full">
        <div className="flex items-center h-full gap-2 pt-2">
          {tabs.map((tab) => {
            const isActive = tab.id === activeTabId;
            return (
              <DropdownMenu key={tab.id}>
                <DropdownMenuTrigger asChild>
                  <div
                    onClick={() => onTabClick(tab.id)}
                    className={cn(
                      "group relative flex items-center h-9 px-4 gap-2 transition-all cursor-pointer text-[12px] font-semibold select-none shrink-0 border-none rounded-xl",
                      isActive 
                        ? "text-primary bg-white shadow-md scale-105 z-10" 
                        : "text-white/70 hover:text-white bg-white/10 backdrop-blur-md border border-white/10 hover:bg-white/20"
                    )}
                  >
                    <div className={cn("transition-colors", isActive ? "text-primary" : "text-white/60")}>
                      {TAB_ICONS[tab.module] || <FileText className="h-3.5 w-3.5" />}
                    </div>
                    <span className="truncate max-w-[120px]">{tab.label}</span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className={cn(
                        "h-4 w-4 p-0 opacity-0 group-hover:opacity-100 rounded-md transition-opacity",
                        isActive ? "opacity-100 text-primary/40 hover:text-primary hover:bg-primary/10" : "text-white/40 hover:text-white hover:bg-white/10"
                      )}
                      onClick={(e) => {
                        e.stopPropagation();
                        onTabClose(tab.id);
                      }}
                    >
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-40">
                  <DropdownMenuItem onClick={() => onTabClose(tab.id)}>
                    Close
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onCloseOthers(tab.id)}>
                    Close Others
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={onCloseAll}>
                    Close All
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            );
          })}
        </div>
        <ScrollBar orientation="horizontal" className="h-1" />
      </ScrollArea>
    </div>
  );
}
