'use client';

import { AppShell } from '@/components/shell/AppShell';

/**
 * Udoo ERP — Main Application Entry
 * 
 * Task 4.1b: Transitioned to a modular Shell architecture.
 * The AppShell orchestrates the ActivityBar, Explorer, Center Panel, 
 * and the VEDA AI co-pilot panel.
 */
export default function Home() {
  return <AppShell />;
}
