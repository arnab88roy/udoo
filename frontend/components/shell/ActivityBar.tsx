'use client';

import { Settings, Home as HomeIcon, Zap, ZapOff } from 'lucide-react';
import { NAV_MODULES } from '@/lib/design-system';
import { VEDAMode } from '@/types/shell';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/theme-toggle';
import { Sparkles } from 'lucide-react';

interface ActivityBarProps {
  activeModule: string;
  onModuleChange: (mod: string) => void;
  visibleModules: string[];
  vedaMode: VEDAMode;
  onVEDAModeChange: (mode: VEDAMode) => void;
  isVEDAOpen: boolean;
  onToggleVEDA: () => void;
}

export function ActivityBar({ 
  activeModule, 
  onModuleChange, 
  visibleModules, 
  vedaMode, 
  onVEDAModeChange,
  isVEDAOpen,
  onToggleVEDA 
}: ActivityBarProps) {
  return (
    <div className="flex flex-col items-center gap-1 pt-3 pb-2 w-12 shrink-0 z-40 bg-transparent border-none antialiased">
      
      {/* Home/Dashboard */}
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onModuleChange('home')}
            className={cn(
              "h-9 w-9 p-0 rounded-xl transition-all duration-200",
              activeModule === 'home' 
                ? "bg-white/10 text-glass-fg-primary shadow-sm ring-1 ring-white/10" 
                : "text-glass-fg-inactive hover:text-glass-fg-primary hover:bg-white/5"
            )}
          >
            <HomeIcon className="h-5 w-5" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="right">Dashboard</TooltipContent>
      </Tooltip>

      <div className="w-8 h-px bg-white/10 my-1" />

      {/* Dynamic Modules */}
      <div className="flex flex-col gap-2">
        {NAV_MODULES.filter(m => visibleModules.includes(m.id)).map((mod) => {
          const Icon = mod.icon;
          return (
            <Tooltip key={mod.id}>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onModuleChange(mod.id)}
                  className={cn(
                    "h-9 w-9 p-0 rounded-xl transition-all duration-200",
                    activeModule === mod.id 
                      ? "bg-white/10 text-glass-fg-primary shadow-sm ring-1 ring-white/10" 
                      : "text-glass-fg-inactive hover:text-glass-fg-primary hover:bg-white/5"
                  )}
                >
                  <Icon className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">{mod.label}</TooltipContent>
            </Tooltip>
          );
        })}
      </div>

      {/* Bottom Actions */}
      <div className="mt-auto flex flex-col items-center gap-4 pb-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button 
              variant="ghost" 
              size="icon" 
              className={cn(
                "h-9 w-9 rounded-xl transition-all duration-200",
                vedaMode === 'auto' ? "bg-white/10 text-glass-fg-primary shadow-sm ring-1 ring-white/10" : "text-white/70 hover:text-white hover:bg-white/5"
              )}
              onClick={() => onVEDAModeChange(vedaMode === 'auto' ? 'assist' : 'auto')}
            >
              {vedaMode === 'auto' ? <Zap className="h-5 w-5 fill-current" /> : <ZapOff className="h-5 w-5" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">Toggle VEDA Mode ({vedaMode})</TooltipContent>
        </Tooltip>

        <ThemeToggle />

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggleVEDA}
              className={cn(
                "h-9 w-9 rounded-xl transition-all duration-300 relative group",
                isVEDAOpen ? "bg-primary/20 text-primary" : "text-glass-fg-inactive hover:text-glass-fg-primary hover:bg-white/5"
              )}
            >
              <div className={cn(
                "absolute inset-0 bg-primary/20 blur-md rounded-full transition-opacity duration-300",
                isVEDAOpen ? "opacity-100" : "opacity-0 group-hover:opacity-50"
              )} />
              <Sparkles className={cn("h-5 w-5 relative z-10", isVEDAOpen ? "animate-pulse" : "")} />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            {isVEDAOpen ? "Close VEDA Assistant" : "Open VEDA Assistant"}
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" className="h-9 w-9 text-glass-fg-inactive hover:text-glass-fg-primary hover:bg-white/5">
              <Settings className="h-5 w-5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">Settings</TooltipContent>
        </Tooltip>

        <Avatar className="h-8 w-8 cursor-pointer ring-1 ring-white/10 hover:ring-2 ring-white/20 transition-all">
          <AvatarFallback className="text-[10px] font-bold bg-white/10 text-glass-fg-primary">AR</AvatarFallback>
        </Avatar>
      </div>
    </div>
  );
}
