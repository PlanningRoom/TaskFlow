import * as TabsPrimitive from '@radix-ui/react-tabs';
import { cn } from '@/lib/cn';

/** Tabs (DRD §8.7 settings, §10.2 project settings). Radix Tabs, token-styled. */
export const Tabs = TabsPrimitive.Root;

export function TabsList({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List className={cn('flex gap-1 border-b border-border', className)} {...props} />
  );
}

export function TabsTrigger({
  className,
  ...props
}: React.ComponentProps<typeof TabsPrimitive.Trigger>) {
  return (
    <TabsPrimitive.Trigger
      className={cn(
        '-mb-px border-b-2 border-transparent px-3 py-2 text-sm font-medium text-text-secondary hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary data-[state=active]:border-primary data-[state=active]:text-primary',
        className,
      )}
      {...props}
    />
  );
}

export function TabsContent({
  className,
  ...props
}: React.ComponentProps<typeof TabsPrimitive.Content>) {
  return (
    <TabsPrimitive.Content
      className={cn('pt-4 focus-visible:outline-none', className)}
      {...props}
    />
  );
}
