import { forwardRef } from 'react';
import { cn } from '@/lib/cn';

/**
 * Form inputs (DRD §7.2). Input/Textarea/Select share resting/focus styling:
 * `--border-input` resting, `--primary` + 3px `--primary-ring` on focus. Set
 * `aria-invalid` to surface the error border.
 */
const base =
  'w-full rounded-sm border border-border-input bg-bg-input px-3 py-[9px] text-sm text-text-primary placeholder:text-text-tertiary focus-visible:border-primary focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-primary aria-[invalid=true]:border-semantic-error disabled:cursor-not-allowed disabled:opacity-50';

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input ref={ref} type={type ?? 'text'} className={cn(base, className)} {...props} />
  ),
);
Input.displayName = 'Input';

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea ref={ref} className={cn(base, 'min-h-20 resize-y', className)} {...props} />
));
Textarea.displayName = 'Textarea';

export const Select = forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => (
    <select ref={ref} className={cn(base, 'cursor-pointer', className)} {...props}>
      {children}
    </select>
  ),
);
Select.displayName = 'Select';

/**
 * A form field label (DRD §7.2: 13px / 500, 6px below). This is a reusable
 * primitive; callers associate it with a control via `htmlFor`/`id` (the
 * association isn't visible to the linter from here).
 */
export function FormLabel({ className, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    // biome-ignore lint/a11y/noLabelWithoutControl: generic label; associated by htmlFor at call sites
    <label
      className={cn('mb-1.5 block text-[13px] font-medium text-text-surface', className)}
      {...props}
    />
  );
}
