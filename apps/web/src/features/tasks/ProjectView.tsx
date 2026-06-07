import { useNavigate } from '@tanstack/react-router';
import { useEffect } from 'react';
import { BoardView } from '@/features/board/BoardView';
import { ListView } from '@/features/list/ListView';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { type ProjectViewKind, setLastView } from '@/lib/projectView';
import { ProjectSubNav } from './ProjectSubNav';
import { TaskDetailPanel } from './TaskDetailPanel';
import type { TaskSearch } from './taskQueryState';
import { searchToParams } from './taskQueryState';

/**
 * Host for the board + list views and the task detail overlay (G3/G4/G5). One
 * component backs all three project routes so the panel genuinely overlays the
 * board/list (which stays mounted behind it, DRD §9). Filter/sort live in the
 * URL search params; the active view is remembered per project (PRD §9.3).
 */
export function ProjectView({
  projectId,
  view,
  search,
  taskId,
}: {
  projectId: string;
  view: ProjectViewKind;
  search: TaskSearch;
  taskId?: string;
}) {
  const navigate = useNavigate();
  const { data: user } = useCurrentUser();
  const params = searchToParams(search);

  // Remember the active view so a bare project URL reopens where you left off.
  useEffect(() => {
    setLastView(projectId, view);
  }, [projectId, view]);

  const boardPath = '/projects/$projectId/board' as const;
  const listPath = '/projects/$projectId/list' as const;

  function setView(next: ProjectViewKind) {
    navigate({ to: next === 'list' ? listPath : boardPath, params: { projectId }, search });
  }
  function setSearch(next: TaskSearch) {
    navigate({
      to: view === 'list' ? listPath : boardPath,
      params: { projectId },
      search: next,
    });
  }
  function openTask(id: string) {
    navigate({
      to: '/projects/$projectId/tasks/$taskId',
      params: { projectId, taskId: id },
      search,
    });
  }
  function closeTask() {
    navigate({ to: view === 'list' ? listPath : boardPath, params: { projectId }, search });
  }

  const role = user?.role ?? 'viewer';

  return (
    <div className="flex h-full min-h-0 flex-col">
      <ProjectSubNav
        projectId={projectId}
        view={view}
        search={search}
        role={role}
        onViewChange={setView}
        onSearchChange={setSearch}
      />
      <div className="min-h-0 flex-1 overflow-auto">
        {view === 'list' ? (
          <ListView
            projectId={projectId}
            params={params}
            search={search}
            role={role}
            onOpenTask={openTask}
            onClearFilters={() => setSearch({ sort: search.sort })}
            onSortChange={(sort) => setSearch({ ...search, sort })}
          />
        ) : (
          <BoardView
            projectId={projectId}
            params={params}
            search={search}
            role={role}
            onOpenTask={openTask}
            onClearFilters={() => setSearch({ sort: search.sort })}
          />
        )}
      </div>
      {taskId ? (
        <TaskDetailPanel projectId={projectId} taskId={taskId} role={role} onClose={closeTask} />
      ) : null}
    </div>
  );
}
