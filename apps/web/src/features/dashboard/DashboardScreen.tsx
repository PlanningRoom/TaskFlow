import { useIntl } from 'react-intl';
import { useWorkspace } from '@/features/settings/useWorkspace';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { MyTasksSection } from './MyTasksSection';
import { ProjectsSection } from './ProjectsSection';
import { RecentActivitySection } from './RecentActivitySection';
import { useMyTasks } from './useDashboard';

/**
 * Dashboard screen (DRD §8.3 / PRD §13). Two-column 60/40 grid (stacks below
 * `lg`): My Tasks on the left; Recent Activity over Projects on the right. A
 * newly-invited user with no assigned tasks yet sees a brief, workspace-named
 * welcome (PRD §3.4); the Owner's first-run "create a project" prompt lives in
 * the Projects panel.
 *
 * Dismissal is keyed on the user's **own** assignments (`my-tasks`), which is the
 * only user-attributable signal available on the client — the workspace activity
 * feed isn't actor-filtered, so using it would hide the welcome the moment an
 * invited user joins an already-active workspace. See PRD §3.4 / DRD §16.
 */
export function DashboardScreen() {
  const intl = useIntl();
  const { data: user } = useCurrentUser();
  const { data: workspace } = useWorkspace();
  const myTasks = useMyTasks();

  const hasTasks = (myTasks.data?.groups ?? []).some((g) => g.tasks.length > 0);
  const showWelcome =
    user !== undefined &&
    user.role !== 'owner' &&
    !!workspace?.name &&
    !myTasks.isPending &&
    !hasTasks;

  return (
    <div className="p-6">
      {showWelcome ? (
        <div className="mb-6 rounded-md border border-border bg-bg-card px-4 py-3">
          <p className="text-[15px] font-semibold text-text-primary">
            {intl.formatMessage(
              { id: 'dashboard.welcome.title' },
              { workspaceName: workspace?.name },
            )}
          </p>
          <p className="mt-0.5 text-[13px] text-text-secondary">
            {intl.formatMessage({ id: 'dashboard.welcome.body' })}
          </p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[3fr_2fr]">
        <MyTasksSection />
        <div className="flex flex-col gap-8">
          <RecentActivitySection />
          {user ? <ProjectsSection role={user.role} /> : null}
        </div>
      </div>
    </div>
  );
}
