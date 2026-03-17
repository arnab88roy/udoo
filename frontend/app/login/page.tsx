"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate navigation/auth
    setTimeout(() => {
      router.push("/dashboard");
    }, 800);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-[var(--color-bg-base)] relative overflow-hidden font-sans">
      {/* Subtle Noise Texture Overlay */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none" 
           style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")` }} 
      />

      <div className="w-full max-w-[400px] space-y-8 animate-in fade-in zoom-in-95 duration-1000 ease-out fill-mode-both">
        <div className="bg-white rounded-[12px] p-10 border border-[var(--color-border)] shadow-[0_8px_32px_rgba(0,0,0,0.04)] relative z-10">
          {/* Logo */}
          <div className="flex flex-col items-center gap-2 mb-8 select-none">
            <div className="flex items-center gap-1.5 translate-x-[-2px]">
              <span className="text-3xl font-bold text-[var(--color-accent-primary)]">U</span>
              <span className="text-xl font-bold text-[var(--color-text-primary)] tracking-tight">udoo</span>
            </div>
            <div className="text-[12px] text-[var(--color-text-secondary)] font-bold tracking-widest uppercase">Your AI-powered ERP</div>
          </div>

          <form onSubmit={handleSignIn} className="space-y-6">
            <div className="text-center space-y-1">
              <h2 className="text-[20px] font-semibold text-[var(--color-text-primary)] tracking-tight">Sign in to Udoo</h2>
            </div>

            <div className="space-y-4 pt-2">
              <div className="space-y-1.5 focus-within:text-[var(--color-accent-primary)] transition-colors">
                <label className="text-[11px] font-bold text-[var(--color-text-secondary)] uppercase tracking-[0.05em] pl-1">Email</label>
                <Input 
                  type="email" 
                  placeholder="name@company.com" 
                  className="h-10 border-[var(--color-border)] focus-visible:ring-1 focus-visible:ring-[var(--color-accent-primary)] text-[14px] bg-[var(--color-bg-base)]/50"
                  required
                />
              </div>
              <div className="space-y-1.5 focus-within:text-[var(--color-accent-primary)] transition-colors">
                <div className="flex justify-between items-center px-1">
                  <label className="text-[11px] font-bold text-[var(--color-text-secondary)] uppercase tracking-[0.05em]">Password</label>
                  <button type="button" className="text-[11px] font-bold text-[var(--color-accent-primary)] hover:underline decoration-2 underline-offset-2">Forgot password?</button>
                </div>
                <Input 
                  type="password" 
                  className="h-10 border-[var(--color-border)] focus-visible:ring-1 focus-visible:ring-[var(--color-accent-primary)] bg-[var(--color-bg-base)]/50"
                  required
                />
              </div>
            </div>

            <Button 
                type="submit"
                disabled={isLoading}
                className="w-full h-10 bg-[var(--color-accent-primary)] hover:bg-[var(--color-accent-hover)] text-white font-bold rounded-[4px] transition-all shadow-md active:scale-[0.98] disabled:opacity-70"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </div>
              ) : "Sign in"}
            </Button>

            <div className="flex items-center gap-4 py-2 opacity-50">
              <Separator className="flex-1" />
              <span className="text-[10px] font-bold text-[var(--color-text-tertiary)] uppercase tracking-[0.2em]">or</span>
              <Separator className="flex-1" />
            </div>

            <Button 
              type="button"
              variant="outline" 
              className="w-full h-10 border-[var(--color-border)] hover:bg-[var(--color-bg-sidebar)] text-[13px] font-bold flex items-center justify-center gap-3 transition-all rounded-[4px] active:scale-[0.98]"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
              </svg>
              Continue with Google
            </Button>
          </form>
        </div>

        <div className="text-center text-[11px] text-[var(--color-text-tertiary)] font-bold select-none tracking-[0.1em] uppercase">
          © 2026 Udoo. Built for Indian SMEs.
        </div>
      </div>
    </div>
  );
}
