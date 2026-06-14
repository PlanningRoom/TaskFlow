import { Link } from '@tanstack/react-router';
import { useIntl } from 'react-intl';
import { Avatar } from '@/components/ui/Avatar';
import { Bell, LayoutGrid, Plus, Settings, UserPlus } from '@/components/ui/icons';
import { CreateProjectModal } from '@/features/dashboard/CreateProjectModal';
import { canCreateProject } from '@/features/dashboard/useDashboard';
import { InviteMemberModal } from '@/features/settings/InviteMemberModal';
import { useInvitations } from '@/features/settings/useInvitations';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { useProjects } from '@/hooks/useProjects';
import { cn } from '@/lib/cn';
import { Logo } from './Logo';

/**
 * Sidebar (DRD §6.3). 240px column: logo, primary nav (Dashboard,
 * Notifications), Projects section (header + `+`, project color dots), and a
 * pinned bottom section (Settings + the user identity block). Link active/hover
 * states use the DRD §6.3 styling. `collapsed` renders the tablet icon-only rail.
 */
const linkClass =
  'flex items-center gap-2.5 rounded-sm px-2.5 py-2 text-sm text-text-sidebar transition-colors hover:bg-bg-hover hover:text-text-primary aria-[current=page]:bg-primary-light aria-[current=page]:text-primary';

export function Sidebar({ collapsed = false }: { collapsed?: boolean }) {
  const { data: user } = useCurrentUser();
  const { data: projectsData } = useProjects();
  const projects = projectsData?.projects ?? [];

  return (
    <aside
      className={cn(
        'flex shrink-0 flex-col border-e border-border-sidebar bg-bg-sidebar',
        collapsed ? 'w-[60px]' : 'w-60',
      )}
    >
      <div className="flex items-center px-4 pb-3 pt-4">
        <Logo markOnly={collapsed} />
      </div>

      <nav className="flex flex-col gap-0.5 px-2">
        <Link to="/dashboard" className={linkClass} title="Dashboard">
          <LayoutGrid size={18} strokeWidth={1.75} className="shrink-0" />
          {!collapsed && <span>Dashboard</span>}
        </Link>
        <Link to="/notifications" className={linkClass} title="Notifications">
          <Bell size={18} strokeWidth={1.75} className="shrink-0" />
          {!collapsed && <span>Notifications</span>}
        </Link>
      </nav>

      {!collapsed && (
        <div className="mt-4 flex min-h-0 flex-1 flex-col px-2">
          <div className="flex items-center justify-between px-2.5 py-1">
            <span className="text-[11px] font-semibold uppercase tracking-[0.05em] text-text-tertiary">
              Projects
            </span>
            {user && canCreateProject(user.role) ? (
              <CreateProjectModal
                trigger={
                  <button
                    type="button"
                    className="rounded-sm p-0.5 text-text-tertiary hover:bg-bg-hover hover:text-text-primary"
                    title="New project"
                    aria-label="New project"
                  >
                    <Plus size={16} strokeWidth={1.75} />
                  </button>
                }
              />
            ) : null}
          </div>
          <div className="flex flex-col gap-0.5 overflow-y-auto">
            {projects.map((p) => (
              <Link
                key={p.id}
                to="/projects/$projectId/board"
                params={{ projectId: p.id }}
                className={linkClass}
              >
                <span
                  className="h-2 w-2 shrink-0 rounded-[2px]"
                  style={{ backgroundColor: p.color ?? 'var(--text-tertiary)' }}
                  aria-hidden
                />
                <span className="truncate">{p.name}</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {!collapsed && user?.role === 'owner' ? <InviteTeamPrompt /> : null}

      <div className={cn('mt-auto border-t border-border-sidebar p-2', collapsed && 'px-1')}>
        <Link to="/settings/workspace" className={linkClass} title="Settings">
          <Settings size={18} strokeWidth={1.75} className="shrink-0" />
          {!collapsed && <span>Settings</span>}
        </Link>
        {user && (
          <div className={cn('mt-1 flex items-center gap-2.5 px-2.5 py-2', collapsed && 'px-1')}>
            <Avatar
              initials={user.initials}
              color={user.avatar_color}
              id={user.id}
              label={user.display_name ?? user.email}
            />
            {!collapsed && (
              <div className="min-w-0">
                <div className="truncate text-[13px] font-medium text-text-primary">
                  {user.display_name ?? user.email}
                </div>
                <div className="text-[11px] capitalize text-text-tertiary">{user.role}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  );
}

/**
 * Owner first-run prompt (PRD §3.4 / DRD §16): "Invite team members", shown in
 * the sidebar until at least one invitation has been sent. Owner-only per the
 * "new workspace (Owner)" framing in PRD §3.4. Visibility is derived from
 * workspace state — it disappears once `invitations` is non-empty, with no
 * backend first-run flag.
 */
function InviteTeamPrompt() {
  const intl = useIntl();
  const { data, isPending } = useInvitations();
  if (isPending || (data?.invitations.length ?? 0) > 0) return null;

  return (
    <div className="mx-2 mb-2">
      <InviteMemberModal
        trigger={
          <button
            type="button"
            className="flex w-full items-center gap-2 rounded-sm border border-dashed border-border-sidebar px-2.5 py-2 text-[13px] text-text-sidebar transition-colors hover:bg-bg-hover hover:text-text-primary"
          >
            <UserPlus size={16} strokeWidth={1.75} className="shrink-0" />
            <span>{intl.formatMessage({ id: 'sidebar.inviteTeam' })}</span>
          </button>
        }
      />
    </div>
  );
}
