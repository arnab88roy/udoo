"use client";

import { EmployeeTable } from "@/components/employees/EmployeeTable";
import { Button } from "@/components/ui/button";
import { Plus, Download, ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export default function EmployeesPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-[20px] font-semibold text-[var(--color-text-primary)] tracking-tight">Employees</h1>
          <p className="text-[13px] text-[var(--color-text-secondary)]">
            24 total · <span className="text-[#137333] font-semibold">22 active</span> · <span className="text-[#E65100] font-semibold">2 on leave</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="h-9 px-4 border-[var(--color-border)] text-[13px] text-[var(--color-text-secondary)] font-semibold bg-white hover:bg-[var(--color-bg-sidebar)] transition-all">
            <Download className="mr-2 h-4 w-4" />
            Import
          </Button>
          <Button className="h-9 px-4 bg-[var(--color-accent-primary)] hover:bg-[var(--color-accent-hover)] text-white text-[13px] font-semibold border-none shadow-[0_1px_2px_rgba(0,0,0,0.1)] transition-all rounded-[4px]">
            <Plus className="mr-2 h-4 w-4" />
            Add Employee
          </Button>
        </div>
      </div>

      {/* Filter Row */}
      <div className="flex items-center gap-3 pt-2">
        <div className="w-72 relative group">
          <Input 
            placeholder="Filter employees..." 
            className="h-8 bg-[var(--color-bg-sidebar)] border-[var(--color-border)] text-[13px] placeholder:text-[var(--color-text-tertiary)] focus-visible:ring-1 focus-visible:ring-[var(--color-accent-primary)] transition-all"
          />
        </div>
        
        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <Button variant="outline" className="h-8 px-3 border-[var(--color-border)] text-[12px] text-[var(--color-text-secondary)] font-semibold min-w-[150px] justify-between hover:bg-[var(--color-bg-sidebar)] transition-all">
                All Departments
                <ChevronDown className="ml-2 h-3 w-3 opacity-50" />
              </Button>
            }
          />
          <DropdownMenuContent align="start" className="w-[180px]">
            <DropdownMenuItem className="text-[13px]">Engineering</DropdownMenuItem>
            <DropdownMenuItem className="text-[13px]">HR</DropdownMenuItem>
            <DropdownMenuItem className="text-[13px]">Sales</DropdownMenuItem>
            <DropdownMenuItem className="text-[13px]">Finance</DropdownMenuItem>
            <DropdownMenuItem className="text-[13px]">Operations</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger
            render={
              <Button variant="outline" className="h-8 px-3 border-[var(--color-border)] text-[12px] text-[var(--color-text-secondary)] font-semibold min-w-[120px] justify-between hover:bg-[var(--color-bg-sidebar)] transition-all">
                All Status
                <ChevronDown className="ml-2 h-3 w-3 opacity-50" />
              </Button>
            }
          />
          <DropdownMenuContent align="start" className="w-[140px]">
            <DropdownMenuItem className="text-[13px]">Active</DropdownMenuItem>
            <DropdownMenuItem className="text-[13px]">On Leave</DropdownMenuItem>
            <DropdownMenuItem className="text-[13px]">Inactive</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Table Area Container with Custom Scroll */}
      <div className="pt-2 overflow-x-auto pb-4">
        <EmployeeTable />
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between px-2 py-4 border-t border-border/40 text-[13px] text-[var(--color-text-secondary)] font-medium">
        <div>Showing 1–8 of 24 employees</div>
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <span>Rows per page:</span>
            <span className="font-bold text-[var(--color-text-primary)] cursor-pointer hover:underline underline-offset-4 decoration-border">25</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" disabled className="h-8 w-8 p-0 text-[var(--color-text-tertiary)] disabled:opacity-40">
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <div className="px-3 h-8 flex items-center justify-center font-bold text-[var(--color-accent-primary)] bg-[#E8F0FE] rounded-md text-[13px]">
              1
            </div>
            <Button variant="ghost" className="h-8 w-8 p-0 text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-sidebar)] transition-colors">
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
