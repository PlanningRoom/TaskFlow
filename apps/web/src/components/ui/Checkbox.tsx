import * as CheckboxPrimitive from '@radix-ui/react-checkbox';
import { cn } from '@/lib/cn';
import { Check } from './icons';

/** Checkbox — Radix Checkbox with token styling and the Lucide check glyph. */
export function Checkbox({
  className,
  ...props
}: React.ComponentProps<typeof CheckboxPrimitive.Root>) {
  return (
    <CheckboxPrimitive.Root
      className={cn(
        'flex h-4 w-4 shrink-0 items-center justify-center rounded-[4px] border border-border-input bg-bg-input focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary data-[state=checked]:border-primary data-[state=checked]:bg-primary data-[state=checked]:text-white disabled:opacity-50',
        className,
      )}
      {...props}
    >
      <CheckboxPrimitive.Indicator>
        <Check size={12} strokeWidth={3} />
      </CheckboxPrimitive.Indicator>
    </CheckboxPrimitive.Root>
  );
}
