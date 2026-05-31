import * as ToastPrimitive from '@radix-ui/react-toast';
import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { cn } from '@/lib/cn';
import { Check } from './icons';

/**
 * Toast (DRD §7.8) — bottom-right, dark surface, green success check, 5s
 * auto-dismiss, fade-up (reduced-motion handled globally in global.css). Built
 * on Radix Toast. Wrap the app in <ToastProvider> and call `useToast().show()`.
 *
 * The richer global store lands in Phase H3; this is the primitive + a minimal
 * context so screens can surface success/error feedback now.
 */
interface ToastItem {
  id: number;
  message: string;
  variant: 'success' | 'error';
}

interface ToastContextValue {
  show: (message: string, variant?: ToastItem['variant']) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within <ToastProvider>');
  return ctx;
}

let nextId = 0;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const show = useCallback((message: string, variant: ToastItem['variant'] = 'success') => {
    setItems((prev) => [...prev, { id: nextId++, message, variant }]);
  }, []);

  const dismiss = useCallback((id: number) => {
    setItems((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const value = useMemo(() => ({ show }), [show]);

  return (
    <ToastContext.Provider value={value}>
      <ToastPrimitive.Provider duration={5000} swipeDirection="right">
        {children}
        {items.map((t) => (
          <ToastPrimitive.Root
            key={t.id}
            onOpenChange={(open) => !open && dismiss(t.id)}
            className={cn(
              'flex items-center gap-2 rounded bg-text-primary px-5 py-3 text-[13px] font-medium text-white shadow-modal',
              'data-[state=open]:animate-in data-[state=closed]:animate-out',
            )}
          >
            {t.variant === 'success' && (
              <Check size={18} className="text-semantic-success" aria-hidden />
            )}
            <ToastPrimitive.Description>{t.message}</ToastPrimitive.Description>
          </ToastPrimitive.Root>
        ))}
        <ToastPrimitive.Viewport className="fixed bottom-6 right-6 z-[999] flex flex-col gap-2 outline-none" />
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  );
}
