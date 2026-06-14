import { type ReactNode, useState } from 'react';
import { Button } from './Button';
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogTrigger } from './Dialog';

/**
 * Destructive-confirmation modal (DRD §18.3): a clear consequence message and a
 * red action button labelled with the verb (never "OK"). Used for remove
 * member, delete label, delete account. Self-contained and controlled: the
 * caller supplies the `trigger`; `onConfirm` runs the action and the dialog
 * closes once it resolves.
 */
export function ConfirmDialog({
  trigger,
  title,
  description,
  confirmLabel,
  cancelLabel = 'Cancel',
  onConfirm,
  pending = false,
}: {
  trigger: ReactNode;
  title: string;
  description: ReactNode;
  confirmLabel: string;
  cancelLabel?: string;
  onConfirm: () => unknown;
  pending?: boolean;
}) {
  const [open, setOpen] = useState(false);

  async function handleConfirm() {
    await onConfirm();
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent title={title}>
        <DialogDescription className="text-[13px] leading-relaxed text-text-secondary">
          {description}
        </DialogDescription>
        <div className="mt-5 flex justify-end gap-2">
          <DialogClose asChild>
            <Button type="button" variant="ghost">
              {cancelLabel}
            </Button>
          </DialogClose>
          <Button
            type="button"
            variant="destructive"
            onClick={handleConfirm}
            disabled={pending}
            aria-busy={pending}
          >
            {confirmLabel}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
