import { useEffect, useState } from 'react';
import { useIntl } from 'react-intl';
import { X } from '@/components/ui/icons';
import { ActivityRow } from '@/features/dashboard/RecentActivitySection';
import { cn } from '@/lib/cn';
import { useProjectActivity } from './useProjectActivity';

/**
 * Project-scope activity side panel (PRD §14.2, plan Open Item #4): reachable
 * from the project sub-nav, slides in from the end edge like the task panel.
 * Backdrop click / Esc / × dismiss it.
 */
export function ProjectActivityPanel({
  projectId,
  onClose,
}: {
  projectId: string;
  onClose: () => void;
}) {
  const intl = useIntl();
  const { data, isPending, isError } = useProjectActivity(projectId);
  const events = data?.events ?? [];

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <button
        type="button"
        aria-label={intl.formatMessage({ id: 'project.activity.closeBackdrop' })}
        className="absolute inset-0 bg-black/25"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={intl.formatMessage({ id: 'project.activity.title' })}
        className={cn(
          'relative flex h-full w-full max-w-[400px] flex-col bg-bg-card shadow-modal transition-transform duration-200 ease-out motion-reduce:transition-none',
          mounted ? 'translate-x-0' : 'translate-x-full',
        )}
      >
        <div className="flex items-center justify-between border-b border-border px-5 py-3.5">
          <h2 className="text-[15px] font-semibold text-text-primary">
            {intl.formatMessage({ id: 'project.activity.title' })}
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label={intl.formatMessage({ id: 'project.activity.close' })}
            className="rounded-sm p-1 text-text-tertiary hover:bg-bg-hover hover:text-text-primary"
          >
            <X size={18} strokeWidth={1.75} />
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-2">
          {isPending ? (
            <p className="py-3 text-[13px] text-text-tertiary">
              {intl.formatMessage({ id: 'app.loading' })}
            </p>
          ) : isError ? (
            <p className="py-3 text-[13px] text-text-secondary">
              {intl.formatMessage({ id: 'project.activity.error' })}
            </p>
          ) : events.length > 0 ? (
            <ul className="flex flex-col">
              {events.map((event) => (
                <ActivityRow key={event.id} event={event} />
              ))}
            </ul>
          ) : (
            <p className="py-3 text-[13px] text-text-secondary">
              {intl.formatMessage({ id: 'project.activity.empty' })}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
