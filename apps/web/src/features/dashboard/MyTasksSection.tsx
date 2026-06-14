import { Link } from '@tanstack/react-router';
import { useIntl } from 'react-intl';
import type { MyTaskGroup } from '@/api/types';
import { DueDate, PriorityIcon, StatusBadge } from '@/components/ui';
import { useProjects } from '@/hooks/useProjects';
import { DashboardNote, DashboardSection } from './DashboardSection';
import { useMyTasks } from './useDashboard';

/**
 * "My tasks" panel (DRD §8.3 / PRD §13.1). Tasks assigned to the caller,
 * grouped by project, overdue first (ordering comes from the backend). Each row
 * links to the task detail panel; overdue due dates render red via {@link DueDate}.
 */
export function MyTasksSection() {
  const intl = useIntl();
  const { data, isPending, isError } = useMyTasks();
  const { data: projectsData } = useProjects();
  const firstProject = projectsData?.projects[0];
  const groups = data?.groups ?? [];
  const hasTasks = groups.some((g) => g.tasks.length > 0);

  return (
    <DashboardSection title={intl.formatMessage({ id: 'dashboard.myTasks.title' })}>
      {isPending ? (
        <DashboardNote>{intl.formatMessage({ id: 'app.loading' })}</DashboardNote>
      ) : isError ? (
        <DashboardNote>{intl.formatMessage({ id: 'dashboard.error' })}</DashboardNote>
      ) : hasTasks ? (
        <div className="flex flex-col gap-5">
          {groups
            .filter((g) => g.tasks.length > 0)
            .map((group) => (
              <TaskGroup key={group.project.id} group={group} />
            ))}
        </div>
      ) : (
        <div className="flex flex-col items-start gap-2">
          <DashboardNote>{intl.formatMessage({ id: 'dashboard.myTasks.empty' })}</DashboardNote>
          {firstProject ? (
            <Link
              to="/projects/$projectId/board"
              params={{ projectId: firstProject.id }}
              className="text-[13px] text-primary underline"
            >
              {intl.formatMessage({ id: 'dashboard.myTasks.browse' })}
            </Link>
          ) : null}
        </div>
      )}
    </DashboardSection>
  );
}

function TaskGroup({ group }: { group: MyTaskGroup }) {
  return (
    <div>
      <h3 className="mb-2 text-xs font-semibold text-text-secondary">{group.project.name}</h3>
      <ul className="flex flex-col gap-1.5">
        {group.tasks.map((task) => (
          <li key={task.id}>
            <Link
              to="/projects/$projectId/tasks/$taskId"
              params={{ projectId: group.project.id, taskId: task.id }}
              className="flex items-center gap-2.5 rounded-sm border border-border bg-bg-card px-3 py-2.5 shadow-card transition-shadow hover:shadow-card-hover"
            >
              <PriorityIcon priority={task.priority} />
              <span className="min-w-0 flex-1 truncate text-[13px] font-medium text-text-primary">
                {task.title}
              </span>
              <StatusBadge status={task.status} />
              <DueDate date={task.due_date} />
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
