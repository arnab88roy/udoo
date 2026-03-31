'use client';
import { useState, useCallback, useEffect, useRef } from 'react';

interface UseResizablePanelOptions {
  defaultWidth: number;
  minWidth: number;
  maxWidth: number;
  storageKey: string;
  side: 'left' | 'right';
}

export function useResizablePanel({
  defaultWidth,
  minWidth,
  maxWidth,
  storageKey,
  side,
}: UseResizablePanelOptions) {
  // Initialize with defaults so server and client render identically (no hydration mismatch).
  // localStorage values are applied after mount in the effect below.
  const [width, setWidth] = useState<number>(defaultWidth);
  const [isOpen, setIsOpen] = useState<boolean>(true);

  const isResizing = useRef(false);
  const startX = useRef(0);
  const startWidth = useRef(0);
  const mounted = useRef(false);

  // Hydrate from localStorage after mount, then allow persist effects to fire
  useEffect(() => {
    const storedWidth = localStorage.getItem(`${storageKey}_width`);
    if (storedWidth) setWidth(Number(storedWidth));

    const storedOpen = localStorage.getItem(`${storageKey}_open`);
    if (storedOpen !== null) setIsOpen(storedOpen === 'true');

    mounted.current = true;
  }, [storageKey]);

  // Persist width (skip default render before hydration)
  useEffect(() => {
    if (!mounted.current) return;
    localStorage.setItem(`${storageKey}_width`, String(width));
  }, [width, storageKey]);

  // Persist isOpen (skip default render before hydration)
  useEffect(() => {
    if (!mounted.current) return;
    localStorage.setItem(`${storageKey}_open`, String(isOpen));
  }, [isOpen, storageKey]);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    isResizing.current = true;
    startX.current = e.clientX;
    startWidth.current = width;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }, [width]);

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (!isResizing.current) return;
      const delta = side === 'left'
        ? e.clientX - startX.current
        : startX.current - e.clientX;
      const newWidth = Math.min(maxWidth, Math.max(minWidth, startWidth.current + delta));
      setWidth(newWidth);
    };

    const onMouseUp = () => {
      if (isResizing.current) {
        isResizing.current = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    return () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };
  }, [minWidth, maxWidth, side]);

  const toggle = useCallback(() => setIsOpen(prev => !prev), []);

  return { width, isOpen, onMouseDown, toggle, setIsOpen };
}
