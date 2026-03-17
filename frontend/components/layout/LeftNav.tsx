"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutGrid, 
  Sparkles, 
  Users, 
  CalendarCheck, 
  Umbrella, 
  IndianRupee, 
  Building, 
  FileText, 
  Receipt, 
  Settings, 
  Shield,
  HelpCircle
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

const NAV_ITEMS = [
  { section: "CORE", items: [
    { label: "Dashboard", icon: LayoutGrid, href: "/dashboard" },
    { label: "VEDA Chat", icon: Sparkles, href: "/dashboard/veda" },
  ]},
  { section: "HRMS", items: [
    { label: "Employees", icon: Users, href: "/dashboard/employees" },
    { label: "Attendance", icon: CalendarCheck, href: "/dashboard/attendance" },
    { label: "Leave", icon: Umbrella, href: "/dashboard/leave" },
    { label: "Payroll", icon: IndianRupee, href: "/dashboard/payroll" },
  ]},
  { section: "FINANCE", items: [
    { label: "Clients", icon: Building, href: "/dashboard/clients" },
    { label: "Quotes", icon: FileText, href: "/dashboard/quotes" },
    { label: "Invoices", icon: Receipt, href: "/dashboard/invoices" },
  ]},
  { section: "SETTINGS", items: [
    { label: "Company", icon: Settings, href: "/dashboard/company" },
    { label: "Compliance", icon: Shield, href: "/dashboard/compliance" },
  ]},
];

export function LeftNav() {
  const pathname = usePathname();

  return (
    <aside className="w-[220px] bg-[var(--color-bg-sidebar)] border-r border-border h-full flex flex-col p-2 relative select-none">
      <div className="flex-1 space-y-4 pt-2 overflow-y-auto">
        {NAV_ITEMS.map((section) => (
          <div key={section.section} className="space-y-1">
            {section.section !== "CORE" && (
              <h3 className="px-3 text-[10px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-wider mb-1 mt-2">
                {section.section}
              </h3>
            )}
            {section.items.map((item) => {
              // Path matches exactly or if dashboard, match /dashboard
              const isActive = pathname === item.href || (item.label === "Employees" && pathname === "/dashboard");
              
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 h-8 rounded-[4px] text-[13px] font-medium transition-colors duration-150",
                    isActive 
                      ? "bg-[#E8F0FE] text-[var(--color-accent-primary)]" 
                      : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-base)]"
                  )}
                >
                  <item.icon className={cn("h-4 w-4 shrink-0", isActive ? "text-[var(--color-accent-primary)]" : "text-[var(--color-text-secondary)]")} />
                  <span className="truncate">{item.label}</span>
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* User profile row at bottom */}
      <div className="mt-auto px-2 pb-4 pt-4 border-t border-border/40">
        <div className="flex items-center justify-between mb-4">
           <div className="flex items-center gap-2">
              <Avatar className="h-6 w-6">
                <AvatarFallback className="bg-orange-100 text-[#E65100] text-[10px] font-bold">A</AvatarFallback>
              </Avatar>
              <span className="text-[13px] font-medium text-[var(--color-text-primary)]">Arnab</span>
           </div>
           <Badge variant="secondary" className="bg-[#F1F3F4] text-[#5F6368] text-[9px] h-4 px-1 leading-none uppercase font-bold">Admin</Badge>
        </div>
        <div className="flex justify-center">
            <HelpCircle className="h-4 w-4 text-[var(--color-text-tertiary)] cursor-pointer hover:text-[var(--color-text-secondary)] transition-colors" />
        </div>
      </div>
    </aside>
  );
}
