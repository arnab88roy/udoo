'use client';

import { 
  Sparkles, 
  PlusCircle, 
  Search, 
  FileText, 
  Users, 
  BarChart2, 
  Clock,
  ArrowRight
} from 'lucide-react';

export function WelcomeScreen() {
  const QUICK_ACTIONS = [
    { label: 'Create Employee', icon: Users, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Apply Leave', icon: Clock, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { label: 'New Invoice', icon: FileText, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'Run Payroll', icon: BarChart2, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-linear-to-b from-(--bg-base) to-(--bg-panel)/10 select-none animate-in fade-in duration-500">
      
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-(--veda-purple)/5 rounded-full blur-[100px] -z-10" />

      {/* Main Content */}
      <div className="max-w-xl w-full flex flex-col items-center gap-8">
        
        {/* Logo Section */}
        <div className="flex flex-col items-center gap-4">
          <div className="w-20 h-20 rounded-3xl bg-linear-to-tr from-(--veda-purple) to-blue-500 flex items-center justify-center p-0.5 shadow-2xl shadow-(--veda-glow) transform hover:rotate-6 transition-transform">
            <div className="w-full h-full rounded-[20px] bg-(--bg-panel) flex items-center justify-center">
              <span className="text-3xl font-black bg-clip-text text-transparent bg-linear-to-tr from-(--veda-purple) to-blue-500">U</span>
            </div>
          </div>
          <div className="text-center space-y-1">
            <h1 className="text-3xl font-black tracking-tighter text-(--text-primary)">
              Welcome to <span className="text-(--veda-purple)">Udoo</span>
            </h1>
            <p className="text-(--text-secondary) text-sm font-medium">
                The AI-Native ERP orchestration engine.
            </p>
          </div>
        </div>

        {/* Global Search / Command Bar */}
        <div className="w-full relative group">
          <div className="absolute -inset-1 bg-linear-to-r from-(--veda-purple) to-blue-500 rounded-2xl blur opacity-10 group-focus-within:opacity-25 transition-opacity duration-500" />
          <div className="relative flex items-center gap-3 bg-(--bg-panel)/80 backdrop-blur-xl border border-(--border-subtle) rounded-2xl px-5 py-4 shadow-2xl shadow-indigo-500/5 focus-within:ring-2 ring-(--veda-purple)/20 transition-all duration-300">
            <Search className="text-(--text-muted) transition-colors group-focus-within:text-(--veda-purple)" size={20} />
            <input 
              type="text" 
              placeholder="Search or ask VEDA (Cmd + K)..."
              className="flex-1 bg-transparent border-none outline-none text-base placeholder:text-(--text-muted)/50"
            />
            <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-(--bg-panel-hover) border border-(--border-subtle)">
               <span className="text-[10px] font-bold text-(--text-muted)">⌘</span>
               <span className="text-[10px] font-bold text-(--text-muted)">K</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="w-full grid grid-cols-2 gap-4">
          {QUICK_ACTIONS.map((action) => (
            <button 
              key={action.label}
              className="group flex items-center gap-4 p-4 rounded-2xl bg-(--bg-panel-hover)/20 border border-(--border-subtle) hover:border-(--veda-purple-border) hover:bg-(--bg-panel-hover)/50 transition-all text-left"
            >
              <div className={`w-12 h-12 rounded-xl ${action.bg} flex items-center justify-center transition-transform group-hover:scale-110`}>
                <action.icon className={action.color} size={24} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[13px] font-bold text-(--text-primary) truncate">{action.label}</p>
                <p className="text-[11px] text-(--text-secondary) opacity-60">Action</p>
              </div>
              <ArrowRight className="text-(--text-muted) opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" size={16} />
            </button>
          ))}
        </div>

        {/* Footer Hint */}
        <div className="flex items-center gap-2 text-[11px] text-(--text-muted) bg-linear-to-r from-transparent via-(--bg-panel-hover) to-transparent px-8 py-2 rounded-full">
            <Sparkles size={12} className="text-(--veda-purple)" />
            <span>Try asking VEDA to <b>run payroll for March</b></span>
        </div>
      </div>
    </div>
  );
}
