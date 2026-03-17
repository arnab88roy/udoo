"use client";

import { ChevronRight, MessageSquare, Send, AtSign, Slash, Sparkles, ArrowUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";

export function VedaSidebar({ 
  isOpen, 
  onToggle 
}: { 
  isOpen: boolean; 
  onToggle: () => void 
}) {
  return (
    <aside 
      className={cn(
        "bg-[var(--color-bg-veda)] border-l border-[var(--color-border-veda)] transition-all duration-200 ease-in-out flex flex-col overflow-hidden shrink-0",
        isOpen ? "w-[340px]" : "w-[48px]"
      )}
    >
      {/* Header */}
      <div className="h-12 border-b border-[var(--color-border-veda)] flex items-center justify-between px-4 shrink-0">
        <div className={cn("flex items-center gap-3 transition-opacity duration-200", !isOpen && "opacity-0")}>
          <div className="relative">
             <div className="h-2 w-2 rounded-full bg-[var(--color-accent-veda)]" />
             <div className="absolute inset-0 h-2 w-2 rounded-full bg-[var(--color-accent-veda)] animate-ping opacity-75" />
          </div>
          <div>
            <div className="text-[13px] font-semibold text-[var(--color-text-veda)] flex items-center gap-1">
              VEDA
            </div>
            <div className="text-[11px] text-[var(--color-text-veda-secondary)]">v0.1 · HR Agent</div>
          </div>
        </div>
        
        {isOpen ? (
          <div className="flex items-center gap-2 shrink-0">
            <button className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--color-bg-veda-input)] text-[var(--color-text-veda-secondary)] border border-[var(--color-border-veda)] hover:text-[var(--color-text-veda)] transition-colors">
               HR Module
            </button>
            <button onClick={onToggle} className="text-[var(--color-text-veda-secondary)] hover:text-[var(--color-text-veda)] p-1 transition-colors">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-6 py-6 h-full w-full">
            <div className="relative">
               <div className="h-2 w-2 rounded-full bg-[var(--color-accent-veda)]" />
               <div className="absolute inset-0 h-2 w-2 rounded-full bg-[var(--color-accent-veda)] animate-ping opacity-75" />
            </div>
            <div className="text-[var(--color-text-veda-secondary)] font-bold text-[10px] rotate-90 mt-2 tracking-[0.2em] whitespace-nowrap">VEDA</div>
            <button onClick={onToggle} className="mt-auto text-[var(--color-text-veda-secondary)] hover:text-[var(--color-text-veda)] p-1 transition-colors">
              <Sparkles className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      {isOpen && (
        <>
          {/* Chat Area */}
          <ScrollArea className="flex-1 px-4 font-mono">
            <div className="py-4 space-y-8">
              {/* Message 1: VEDA */}
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className="h-5 w-5 rounded-full bg-[var(--color-accent-veda)] flex items-center justify-center text-[10px] text-white font-bold select-none">V</div>
                  <span className="text-[10px] font-bold text-[var(--color-text-veda-secondary)] uppercase tracking-wider">VEDA</span>
                </div>
                <div className="text-[13px] text-[var(--color-text-veda)] leading-[1.6] space-y-4">
                  <p>Good morning, Arnab 👋</p>
                  <p>I'm VEDA, your enterprise copilot for Udoo.</p>
                  <div className="space-y-1 pl-3 border-l-2 border-[var(--color-border-veda)]">
                    <p>I can help you with:</p>
                    <p>▸ Employee management & onboarding</p>
                    <p>▸ Leave and attendance tracking</p>
                    <p>▸ Payroll processing & compliance</p>
                    <p>▸ Quotes, invoices & GST</p>
                  </div>
                  <p>What would you like to do today?</p>
                </div>
              </div>

              {/* Message 2: User */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '12px' }}>
                <div style={{
                  background: 'var(--color-accent-primary)',
                  color: '#FFFFFF',
                  borderRadius: '16px 16px 4px 16px',
                  padding: '8px 12px',
                  maxWidth: '80%',
                  fontSize: '13px',
                  fontFamily: 'JetBrains Mono, monospace',
                  lineHeight: '1.5',
                  wordBreak: 'break-word'
                }}>
                  Generate salary slips for March 2026
                </div>
              </div>

              {/* Message 3: VEDA */}
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className="h-5 w-5 rounded-full bg-[var(--color-accent-veda)] flex items-center justify-center text-[10px] text-white font-bold select-none">V</div>
                  <span className="text-[10px] font-bold text-[var(--color-text-veda-secondary)] uppercase tracking-wider">VEDA</span>
                </div>
                <div className="text-[13px] text-[var(--color-text-veda)] leading-[1.6] space-y-4">
                  <p>I'll process payroll for March 2026. Let me check the status first.</p>
                  <div className="space-y-1 text-[12px] text-[var(--color-text-veda-secondary)]">
                    <div className="flex items-center gap-2"><span className="text-[var(--color-accent-veda)] font-bold">✓</span> Fetching active employees... 22 found</div>
                    <div className="flex items-center gap-2"><span className="text-[var(--color-accent-veda)] font-bold">✓</span> Checking attendance records... Complete</div>
                    <div className="flex items-center gap-2"><span className="text-[#FFB340] font-bold">⚠</span> Verifying salary structures... 2 employees missing structure</div>
                  </div>
                  <p>Before I generate, I need your confirmation:</p>
                  <div className="bg-[var(--color-bg-veda-input)] border border-[var(--color-border-veda)] rounded-lg p-3.5 text-[11px] space-y-2 font-mono">
                    <div className="text-[var(--color-text-veda-secondary)] mb-2 border-b border-[var(--color-border-veda)] pb-2 font-bold uppercase tracking-wide">Payroll Summary — March 2026</div>
                    <div className="flex justify-between"><span>Employees:</span> <span className="text-white">22</span></div>
                    <div className="flex justify-between"><span>Working days:</span> <span className="text-white">26</span></div>
                    <div className="flex justify-between"><span>Est. gross:</span> <span className="text-white">₹4,82,000</span></div>
                    <div className="flex justify-between"><span>Est. PF:</span> <span className="text-white">₹39,600</span></div>
                    <div className="flex justify-between"><span>Est. ESI:</span> <span className="text-white">₹3,615</span></div>
                  </div>
                  <p>Shall I proceed with the 20 employees who have structures set up, and flag the other 2 for your review?</p>
                </div>
              </div>

              {/* Message 4: User */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '12px' }}>
                <div style={{
                  background: 'var(--color-accent-primary)',
                  color: '#FFFFFF',
                  borderRadius: '16px 16px 4px 16px',
                  padding: '8px 12px',
                  maxWidth: '80%',
                  fontSize: '13px',
                  fontFamily: 'JetBrains Mono, monospace',
                  lineHeight: '1.5',
                  wordBreak: 'break-word'
                }}>
                  Yes, proceed
                </div>
              </div>

              {/* Message 5: VEDA (Progress State) */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{
                  fontSize: '13px',
                  fontFamily: 'JetBrains Mono, monospace',
                  color: 'var(--color-text-veda)',
                  marginBottom: '8px',
                  lineHeight: 1.6
                }}>
                  Generating salary slips...
                </div>
                
                {/* Progress track */}
                <div style={{
                  background: '#3A3A3C',
                  borderRadius: '4px',
                  height: '6px',
                  width: '100%',
                  overflow: 'hidden',
                  marginBottom: '6px'
                }}>
                  {/* Progress fill — animate with CSS */}
                  <div style={{
                    height: '100%',
                    width: '67%',
                    background: 'var(--color-accent-veda)',  // green
                    borderRadius: '4px',
                    animation: 'progressFill 1.2s ease-out forwards'
                  }} />
                </div>
                
                <div style={{
                  fontSize: '11px',
                  fontFamily: 'JetBrains Mono, monospace',
                  color: 'var(--color-text-veda-secondary)'
                }}>
                  67% — Processing Rahul Mehta
                </div>
              </div>
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div style={{
            borderTop: '1px solid var(--color-border-veda)',
            background: 'var(--color-bg-veda-input)',
            padding: '12px',
            flexShrink: 0
          }}>
            {/* Action chips row */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <button style={{
                background: '#2C2C2E',
                border: '1px solid #3A3A3C',
                borderRadius: '12px',
                padding: '4px 10px',
                fontSize: '11px',
                color: 'var(--color-text-veda-secondary)',
                cursor: 'pointer',
                fontFamily: 'JetBrains Mono, monospace'
              }}>
                Review flagged employees →
              </button>
              <button style={{
                background: '#2C2C2E',
                border: '1px solid #3A3A3C',
                borderRadius: '12px',
                padding: '4px 10px',
                fontSize: '11px',
                color: 'var(--color-text-veda-secondary)',
                cursor: 'pointer',
                fontFamily: 'JetBrains Mono, monospace'
              }}>
                Download report →
              </button>
            </div>

            {/* Input row */}
            <div style={{
              display: 'flex',
              alignItems: 'flex-end',
              gap: '8px'
            }}>
              <textarea
                placeholder="Ask VEDA anything..."
                rows={1}
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: 'var(--color-text-veda)',
                  fontSize: '13px',
                  fontFamily: 'JetBrains Mono, monospace',
                  resize: 'none',
                  lineHeight: '1.5',
                  paddingTop: '2px'
                }}
              />
              <button style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: 'var(--color-accent-primary)',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <ArrowUp size={14} color="white" />
              </button>
            </div>
          </div>
        </>
      )}
    </aside>
  );
}
