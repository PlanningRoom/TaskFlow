import { Link } from '@tanstack/react-router';
import { useIntl } from 'react-intl';
import type { CurrentUser, DashboardProject } from '@/api/types';
import { Button } from '@/components/ui';
import { Plus } from '@/components/ui/icons';
import { CreateProjectModal } from './CreateProjectModal';
import { DashboardNote, DashboardSection } from './DashboardSection';
import { canCreateProject, useDashboardProjects } from './useDashboard';

/**
 * "Projects" panel (DRD §8.3 / PRD §13.3). Visible projects with a per-status
 * task-count summary; each row opens the board. The empty state doubles as the
 * Owner first-run "Create your first project" prompt (PRD §3.4), role-gated so
 * Viewers see the message without a CTA.
 */
export function ProjectsSection({ role }: { role: CurrentUser['role'] }) {
  const intl = useIntl();
  const { data, isPending, isError } = useDashboardProjects();
  const projects = data?.projects ?? [];

  return (
    <DashboardSection title={intl.formatMessage({ id: 'dashboard.projects.title' })}>
      {isPending ? (
        <DashboardNote>{intl.formatMessage({ id: 'app.loading' })}</DashboardNote>
      ) : isError ? (
        <DashboardNote>{intl.formatMessage({ id: 'dashboard.error' })}</DashboardNote>
      ) : projects.length > 0 ? (
        <ul className="flex flex-col gap-1.5">
          {projects.map((project) => (
            <ProjectRow key={project.id} project={project} />
          ))}
        </ul>
      ) : (
        <div className="flex flex-col items-start gap-3">
          <DashboardNote>{intl.formatMessage({ id: 'dashboard.projects.empty' })}</DashboardNote>
          {canCreateProject(role) ? (
            <CreateProjectModal
              trigger={
                <Button>
                  <Plus size={16} strokeWidth={1.75} />
                  {intl.formatMessage({ id: 'dashboard.projects.createFirst' })}
                </Button>
              }
            />
          ) : null}
        </div>
      )}
    </DashboardSection>
  );
}

function ProjectRow({ project }: { project: DashboardProject }) {
  const intl = useIntl();
  const counts = project.task_counts;
  const total =
    counts.backlog +
    counts.todo +
    counts.in_progress +
    counts.in_review +
    counts.done +
    counts.cancelled;

  return (
    <li>
      <Link
        to="/projects/$projectId/board"
        params={{ projectId: project.id }}
        className="flex items-center gap-2.5 rounded-sm border border-border bg-bg-card px-3 py-2.5 shadow-card transition-shadow hover:shadow-card-hover"
      >
        <span
          className="h-2.5 w-2.5 shrink-0 rounded-[3px]"
          style={{ backgroundColor: project.color ?? 'var(--text-tertiary)' }}
          aria-hidden
        />
        <span className="min-w-0 flex-1 truncate text-[13px] font-medium text-text-primary">
          {project.name}
        </span>
        <span className="shrink-0 text-[11px] text-text-tertiary">
          {intl.formatMessage({ id: 'dashboard.projects.taskCount' }, { total, done: counts.done })}
        </span>
      </Link>
    </li>
  );
}
