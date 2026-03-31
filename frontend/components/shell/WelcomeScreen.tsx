import { 
  Sparkles, 
  PlusCircle, 
  Search, 
  FileText, 
  Users, 
  BarChart2, 
  Clock,
  ArrowRight,
  Command,
  Layout
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export function WelcomeScreen() {
  const QUICK_ACTIONS = [
    { label: 'Create Employee', icon: Users, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Apply Leave', icon: Clock, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { label: 'New Invoice', icon: FileText, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'Run Payroll', icon: BarChart2, color: 'text-primary', bg: 'bg-primary/10' },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-transparent relative overflow-hidden select-none animate-in fade-in duration-700">
      
      {/* Dynamic Background Elements */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/3 rounded-full blur-[100px] animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/3 rounded-full blur-[120px] animate-pulse delay-700" />

      {/* Main Content Container */}
      <div className="max-w-2xl w-full flex flex-col items-center gap-10 z-10">
        
        {/* Branding & Header */}
        <div className="flex flex-col items-center gap-6 text-center">
          <div className="relative group">
            <div className="absolute -inset-1.5 bg-linear-to-tr from-primary to-blue-600 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-500" />
            <div className="relative w-20 h-20 rounded-2xl bg-white border-none flex items-center justify-center shadow-xl transition-transform group-hover:scale-105 duration-300">
              <span className="text-4xl font-black bg-clip-text text-transparent bg-linear-to-tr from-primary to-blue-600">U</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
              Hello, <span className="text-primary italic">Udoo</span>
            </h1>
            <p className="text-muted-foreground text-base max-w-md font-medium mx-auto">
              Your AI-orchestrated enterprise workspace is ready.
              Efficiency starts here.
            </p>
          </div>
        </div>

        {/* Command Search Bar */}
        <div className="w-full max-w-lg relative group">
          <div className="absolute -inset-0.5 bg-linear-to-r from-primary/20 to-blue-500/20 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
          <div className="relative flex items-center px-4 bg-muted/30 border-none rounded-xl shadow-none transition-all duration-300">
            <Search className="h-5 w-5 text-muted-foreground mr-3" />
            <Input 
              placeholder="Search or ask VEDA (Ctrl + K)..."
              className="h-14 border-none bg-transparent shadow-none focus-visible:ring-0 text-base placeholder:text-muted-foreground/50"
            />
            <div className="flex items-center gap-1 px-1.5 py-0.5 rounded border border-border bg-background text-[10px] font-bold text-muted-foreground shadow-sm">
              <Command className="h-2.5 w-2.5" />
              <span>K</span>
            </div>
          </div>
        </div>

        {/* Quick Action Grid */}
        <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-4">
          {QUICK_ACTIONS.map((action) => (
            <Card 
              key={action.label} 
              className="overflow-hidden border-none bg-muted/10 hover:bg-muted/20 transition-all duration-300 cursor-pointer group shadow-none hover:shadow-none"
            >
              <CardContent className="p-4 flex items-center gap-4">
                <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center shrink-0 transition-transform group-hover:scale-110 duration-300", action.bg)}>
                  <action.icon className={cn("h-6 w-6", action.color)} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-bold text-foreground mb-0.5">{action.label}</h3>
                  <p className="text-[11px] text-muted-foreground line-clamp-1">Ready to process</p>
                </div>
                <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Suggestion Badge */}
        <div className="flex items-center animate-in slide-in-from-bottom-4 duration-1000">
          <Badge variant="outline" className="px-4 py-2 bg-muted/30 border-dashed border-primary/30 text-muted-foreground hover:bg-muted/50 transition-colors">
            <Sparkles className="h-3.5 w-3.5 mr-2 text-primary" />
            <span className="text-[11px] font-medium tracking-wide lowercase">
              Try asking VEDA: <span className="text-foreground font-bold italic">"summarize employee counts by department"</span>
            </span>
          </Badge>
        </div>

      </div>
    </div>
  );
}
