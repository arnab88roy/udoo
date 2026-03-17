"use client";

import { useState, useEffect } from "react";
import { TopBar } from "@/components/layout/TopBar";
import { LeftNav } from "@/components/layout/LeftNav";
import { VedaSidebar } from "@/components/layout/VedaSidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [vedaOpen, setVedaOpen] = useState(true);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setVedaOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[var(--color-bg-base)] font-sans antialiased text-[var(--color-text-primary)]">
      <TopBar vedaOpen={vedaOpen} onVedaToggle={() => setVedaOpen(!vedaOpen)} />
      
      <div className="flex flex-1 overflow-hidden relative">
        <LeftNav />
        
        <main className="flex-1 overflow-y-auto bg-white relative">
          <div className="min-w-[800px] max-w-7xl mx-auto p-8">
            {children}
          </div>
        </main>

        <VedaSidebar isOpen={vedaOpen} onToggle={() => setVedaOpen(!vedaOpen)} />
      </div>
    </div>
  );
}
