import type { ReactNode } from 'react';

/**
 * Shared dashboard section frame (DRD §8.3): a 15px semibold heading over the
 * section body. `action` renders at the end of the heading row (e.g. a link).
 */
export function DashboardSection({
  title,
  action,
  children,
}: {
  title: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-[15px] font-semibold text-text-primary">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

/** A muted single-line empty/loading message used across dashboard sections. */
export function DashboardNote({ children }: { children: ReactNode }) {
  return <p className="text-[13px] text-text-secondary">{children}</p>;
}
