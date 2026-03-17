"use client";

import { MoreVertical } from "lucide-react";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const EMPLOYEES = [
  { id: "EMP-001", name: "Priya Sharma", department: "Engineering", designation: "Senior Developer", status: "Active", joined: "Jan 2022", color: "bg-blue-100 text-blue-600" },
  { id: "EMP-002", name: "Rahul Mehta", department: "Engineering", designation: "Backend Engineer", status: "Active", joined: "Mar 2023", color: "bg-purple-100 text-purple-600" },
  { id: "EMP-003", name: "Anjali Patel", department: "HR", designation: "HR Manager", status: "Active", joined: "Jun 2021", color: "bg-pink-100 text-pink-600" },
  { id: "EMP-004", name: "Vikram Singh", department: "Sales", designation: "Sales Executive", status: "On Leave", joined: "Nov 2022", color: "bg-orange-100 text-orange-600" },
  { id: "EMP-005", name: "Neha Gupta", department: "Finance", designation: "Accounts Manager", status: "Active", joined: "Feb 2023", color: "bg-green-100 text-green-600" },
  { id: "EMP-006", name: "Arjun Nair", department: "Engineering", designation: "Frontend Developer", status: "Active", joined: "Jul 2023", color: "bg-indigo-100 text-indigo-600" },
  { id: "EMP-007", name: "Sunita Rao", department: "Operations", designation: "Operations Lead", status: "Active", joined: "Apr 2021", color: "bg-cyan-100 text-cyan-600" },
  { id: "EMP-008", name: "Karan Shah", department: "Sales", designation: "Sales Manager", status: "Inactive", joined: "Sep 2020", color: "bg-gray-100 text-gray-600" },
];

export function EmployeeTable() {
  return (
    <div className="w-full border border-border rounded-lg overflow-hidden bg-white shadow-[0_1px_3px_rgba(0,0,0,0.08)]">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-[var(--color-bg-sidebar)] border-b border-border h-10 select-none">
            <th className="px-4 w-10 text-center">
              <input type="checkbox" className="rounded border-border" />
            </th>
            <th className="px-4 text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-widest font-sans">Employee</th>
            <th className="px-4 text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-widest font-sans">Department</th>
            <th className="px-4 text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-widest font-sans">Designation</th>
            <th className="px-4 text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-widest font-sans">Status</th>
            <th className="px-4 text-[10px] font-bold text-[var(--color-text-secondary)] uppercase tracking-widest font-sans">Joined</th>
            <th className="px-4 w-10"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60">
          {EMPLOYEES.map((employee, idx) => (
            <tr 
              key={employee.id} 
              className="h-12 border-b border-border hover:bg-[var(--color-bg-base)] transition-colors group animate-in fade-in slide-in-from-bottom-2 duration-400 fill-mode-both"
              style={{ animationDelay: `${idx * 40}ms` }}
            >
              <td className="px-4 text-center">
                <input type="checkbox" className="rounded border-border cursor-pointer" />
              </td>
              <td className="px-4 py-2">
                <div className="flex items-center gap-3">
                  <Avatar className="h-8 w-8 border border-border/20">
                    <AvatarFallback className={cn("text-[10px] font-bold uppercase", employee.color)}>
                      {employee.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="text-[13px] font-semibold text-[var(--color-text-primary)]">{employee.name}</div>
                    <div className="text-[10px] text-[var(--color-text-tertiary)] font-bold tracking-tight">{employee.id}</div>
                  </div>
                </div>
              </td>
              <td className="px-4 text-[13px] text-[var(--color-text-secondary)] font-medium">{employee.department}</td>
              <td className="px-4 text-[13px] text-[var(--color-text-secondary)] font-medium">{employee.designation}</td>
              <td className="px-4">
                <span className={cn(
                  "px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-tight inline-block text-center min-w-[70px]",
                  employee.status === "Active" && "bg-[#E6F4EA] text-[#137333]",
                  employee.status === "On Leave" && "bg-[#FFF3E0] text-[#E65100]",
                  employee.status === "Inactive" && "bg-[#F1F3F4] text-[#5F6368]"
                )}>
                  {employee.status}
                </span>
              </td>
              <td className="px-4 text-[13px] text-[var(--color-text-secondary)] font-medium">{employee.joined}</td>
              <td className="px-4 text-center opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="p-1.5 hover:bg-gray-100 rounded-full transition-colors">
                  <MoreVertical className="h-4 w-4 text-[var(--color-text-tertiary)]" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
