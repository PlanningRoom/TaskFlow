import { Link, useNavigate } from '@tanstack/react-router';
import { type ReactNode, useEffect } from 'react';
import { useIntl } from 'react-intl';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { cn } from '@/lib/cn';

/**
 * Settings shell (DRD §8.7): a tab strip over the active settings page.
 * Workspace/Members/Labels are Owner/Admin-only and redirect everyone else to
 * the dashboard; Profile is open to all. The tab strip hides manage-only tabs
 * from Members/Viewers.
 */
type SettingsTab = 'workspace' | 'members' | 'labels' | 'profile';

const TABS: { key: SettingsTab; to: string; labelId: string; manage: boolean }[] = [
  { key: 'workspace', to: '/settings/workspace', labelId: 'settings.tab.workspace', manage: true },
  { key: 'members', to: '/settings/members', labelId: 'settings.tab.members', manage: true },
  { key: 'labels', to: '/settings/labels', labelId: 'settings.tab.labels', manage: true },
  { key: 'profile', to: '/settings/profile', labelId: 'settings.tab.profile', manage: false },
];

export function SettingsLayout({
  tab,
  requiresManage,
  children,
}: {
  tab: SettingsTab;
  requiresManage: boolean;
  children: ReactNode;
}) {
  const intl = useIntl();
  const navigate = useNavigate();
  const { data: user } = useCurrentUser();
  const canManage = user?.role === 'owner' || user?.role === 'admin';

  // Members/Viewers can't see manage-only pages — bounce them to the dashboard.
  useEffect(() => {
    if (requiresManage && user && !canManage) navigate({ to: '/dashboard' });
  }, [requiresManage, user, canManage, navigate]);
  if (requiresManage && user && !canManage) return null;

  const tabs = TABS.filter((t) => !t.manage || canManage);

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="mb-4 text-[17px] font-semibold text-text-primary">
        {intl.formatMessage({ id: 'settings.title' })}
      </h1>
      <nav className="mb-6 flex gap-1 border-b border-border" aria-label="Settings">
        {tabs.map((t) => (
          <Link
            key={t.key}
            to={t.to}
            className={cn(
              '-mb-px border-b-2 px-3 py-2 text-[13px]',
              t.key === tab
                ? 'border-primary font-medium text-text-primary'
                : 'border-transparent text-text-secondary hover:text-text-primary',
            )}
          >
            {intl.formatMessage({ id: t.labelId })}
          </Link>
        ))}
      </nav>
      {children}
    </div>
  );
}
