import * as TooltipPrimitive from '@radix-ui/react-tooltip';
import { cn } from '@/lib/cn';

/** Tooltip — Radix Tooltip, token-styled. Wrap the app once in `TooltipProvider`. */
export const TooltipProvider = TooltipPrimitive.Provider;
export const Tooltip = TooltipPrimitive.Root;
export const TooltipTrigger = TooltipPrimitive.Trigger;

export function TooltipContent({
  className,
  sideOffset = 6,
  ...props
}: React.ComponentProps<typeof TooltipPrimitive.Content>) {
  return (
    <TooltipPrimitive.Portal>
      <TooltipPrimitive.Content
        sideOffset={sideOffset}
        className={cn(
          'z-50 rounded-sm bg-text-primary px-2 py-1 text-xs font-medium text-white shadow-dropdown',
          className,
        )}
        {...props}
      />
    </TooltipPrimitive.Portal>
  );
}
