import * as DialogPrimitive from '@radix-ui/react-dialog';
import { cn } from '@/lib/cn';
import { X } from './icons';

/**
 * Dialog (DRD §10 modal base). Radix Dialog with token styling: centered card,
 * `--radius-lg`, `--shadow-modal`, dimmed backdrop. Backdrop click + Esc close
 * (Radix default); an explicit × is provided in the header.
 */
export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

export function DialogContent({
  className,
  children,
  title,
  ...props
}: React.ComponentProps<typeof DialogPrimitive.Content> & { title: string }) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/30" />
      <DialogPrimitive.Content
        className={cn(
          'fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-lg bg-bg-card p-5 shadow-modal focus:outline-none',
          className,
        )}
        {...props}
      >
        <div className="mb-4 flex items-center justify-between">
          <DialogPrimitive.Title className="text-base font-semibold text-text-primary">
            {title}
          </DialogPrimitive.Title>
          <DialogPrimitive.Close
            className="rounded-sm p-1 text-text-tertiary hover:bg-bg-hover hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="Close"
          >
            <X size={18} />
          </DialogPrimitive.Close>
        </div>
        {children}
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

/** Optional visually-hidden description for a11y when content needs one. */
export const DialogDescription = DialogPrimitive.Description;
