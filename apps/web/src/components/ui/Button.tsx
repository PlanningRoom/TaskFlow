import { cva, type VariantProps } from 'class-variance-authority';
import { forwardRef } from 'react';
import { cn } from '@/lib/cn';

/**
 * Button (DRD §7.1). Variants primary/secondary/ghost/destructive; sizes
 * standard + sm. Token-driven so a theme swap needs no changes here.
 */
const button = cva(
  'inline-flex items-center justify-center gap-2 rounded-sm font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-white hover:bg-primary-hover',
        secondary: 'border border-primary bg-transparent text-primary hover:bg-primary-light',
        ghost: 'bg-transparent text-text-secondary hover:bg-bg-hover hover:text-text-primary',
        destructive: 'bg-semantic-error text-white hover:brightness-95',
      },
      size: {
        // DRD §7.1: standard 9px 16px @ 14/500; small 6px 10px @ 12.
        md: 'px-4 py-[9px] text-sm',
        sm: 'px-[10px] py-[6px] text-xs',
      },
      full: { true: 'w-full', false: '' },
    },
    defaultVariants: { variant: 'primary', size: 'md', full: false },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof button> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, full, type, ...props }, ref) => (
    <button
      ref={ref}
      type={type ?? 'button'}
      className={cn(button({ variant, size, full }), className)}
      {...props}
    />
  ),
);
Button.displayName = 'Button';
