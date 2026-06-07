import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type {
  CreateProjectRequest,
  CurrentUser,
  DashboardProjectsResponse,
  ListActivityResponse,
  MyTasksResponse,
  Project,
} from '@/api/types';
import { PROJECTS_KEY } from '@/hooks/useProjects';

/**
 * Data hooks for the Phase G2 dashboard. Each wraps the backend's dashboard /
 * activity endpoints (Phases C5, C8) via {@link useApiQuery}; `useCreateProject`
 * powers the Create Project modal (DRD §10.1) shared with the sidebar `+`.
 */

/** Roles allowed to create a project (PRD §5.1) — everyone except Viewer. */
export function canCreateProject(role: CurrentUser['role']): boolean {
  return role !== 'viewer';
}

export const MY_TASKS_KEY = ['dashboard', 'my-tasks'] as const;
export const DASHBOARD_PROJECTS_KEY = ['dashboard', 'projects'] as const;
export const WORKSPACE_ACTIVITY_KEY = ['activity', 'workspace'] as const;

/** Tasks assigned to the caller, grouped by project, overdue first (C8). */
export function useMyTasks() {
  return useApiQuery<MyTasksResponse>({
    queryKey: MY_TASKS_KEY,
    queryFn: () => apiClient.get<MyTasksResponse>('/dashboard/my-tasks'),
  });
}

/** Visible projects with per-status task counts (C8). */
export function useDashboardProjects() {
  return useApiQuery<DashboardProjectsResponse>({
    queryKey: DASHBOARD_PROJECTS_KEY,
    queryFn: () => apiClient.get<DashboardProjectsResponse>('/dashboard/projects'),
  });
}

/** Recent activity at workspace scope, first page only (C5). */
export function useDashboardActivity() {
  return useApiQuery<ListActivityResponse>({
    queryKey: WORKSPACE_ACTIVITY_KEY,
    queryFn: () => apiClient.get<ListActivityResponse>('/activity'),
  });
}

/**
 * Create a project (C2). On success, refresh both the sidebar project list and
 * the dashboard projects panel; the caller handles the toast + navigation so it
 * has the returned project to route to.
 */
export function useCreateProject() {
  const queryClient = useQueryClient();
  return useApiMutation<Project, CreateProjectRequest>({
    mutationFn: (body) => apiClient.post<Project>('/projects', body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: PROJECTS_KEY });
      void queryClient.invalidateQueries({ queryKey: DASHBOARD_PROJECTS_KEY });
    },
  });
}
