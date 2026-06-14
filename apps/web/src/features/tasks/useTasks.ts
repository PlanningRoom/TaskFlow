import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type {
  CreateTaskRequest,
  ListTasksResponse,
  TaskDetail,
  TaskSummary,
  UpdateStatusRequest,
  UpdateTaskRequest,
} from '@/api/types';

/**
 * Task data hooks (Phases C3). Board + list read `useProjectTasks`; the detail
 * panel reads `useTask`. `useUpdateTaskStatus` is optimistic (ADR 046): it
 * patches every cached task list for the project, rolling back on error.
 */

export type TaskStatus = TaskSummary['status'];
export type TaskPriority = TaskSummary['priority'];
export type DueFilter = 'overdue' | 'today' | 'this_week' | 'no_due_date';
export type TaskSort = 'created_at' | 'priority' | 'due_date' | 'assignee';

/** Filter + sort state shared by board and list (mirrors the backend params). */
export interface TaskQueryParams {
  status?: TaskStatus[];
  assignee?: string[];
  priority?: TaskPriority[];
  label?: string[];
  due?: DueFilter;
  include_cancelled?: boolean;
  sort?: TaskSort;
}

export const tasksKey = (projectId: string, params?: TaskQueryParams) =>
  ['tasks', projectId, params ?? {}] as const;
export const taskKey = (taskId: string) => ['task', taskId] as const;

/** Tasks in a project, filtered + sorted (board/list). */
export function useProjectTasks(projectId: string, params: TaskQueryParams) {
  return useApiQuery<ListTasksResponse>({
    queryKey: tasksKey(projectId, params),
    queryFn: () =>
      apiClient.get<ListTasksResponse>(`/projects/${projectId}/tasks`, {
        query: {
          status: params.status,
          assignee: params.assignee,
          priority: params.priority,
          label: params.label,
          due: params.due,
          include_cancelled: params.include_cancelled ? true : undefined,
          sort: params.sort,
        },
      }),
  });
}

/** Single task with description + timestamps (detail panel). */
export function useTask(taskId: string) {
  return useApiQuery<TaskDetail>({
    queryKey: taskKey(taskId),
    queryFn: () => apiClient.get<TaskDetail>(`/tasks/${taskId}`),
  });
}

export function useCreateTask(projectId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<TaskDetail, CreateTaskRequest>({
    mutationFn: (body) => apiClient.post<TaskDetail>(`/projects/${projectId}/tasks`, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
    },
  });
}

export function useUpdateTask(taskId: string, projectId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<TaskDetail, UpdateTaskRequest>({
    mutationFn: (body) => apiClient.patch<TaskDetail>(`/tasks/${taskId}`, body),
    onSuccess: (task) => {
      queryClient.setQueryData(taskKey(taskId), task);
      void queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
    },
  });
}

interface StatusVars {
  taskId: string;
  status: TaskStatus;
}

/**
 * Optimistic status change (ADR 046) used by board drag-and-drop and the inline
 * list/panel status dropdowns. Patches the task in every cached list for the
 * project + the single-task cache; rolls all of them back on error.
 */
export function useUpdateTaskStatus(projectId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<TaskDetail, StatusVars>({
    mutationFn: ({ taskId, status }) =>
      apiClient.patch<TaskDetail>(`/tasks/${taskId}/status`, {
        status,
      } satisfies UpdateStatusRequest),
    onMutate: async ({ taskId, status }) => {
      await queryClient.cancelQueries({ queryKey: ['tasks', projectId] });
      const lists = queryClient.getQueriesData<ListTasksResponse>({
        queryKey: ['tasks', projectId],
      });
      for (const [key, data] of lists) {
        if (!data) continue;
        queryClient.setQueryData<ListTasksResponse>(key, {
          ...data,
          tasks: data.tasks.map((t) => (t.id === taskId ? { ...t, status } : t)),
        });
      }
      const prevTask = queryClient.getQueryData<TaskDetail>(taskKey(taskId));
      if (prevTask) queryClient.setQueryData(taskKey(taskId), { ...prevTask, status });
      return { lists, prevTask };
    },
    onError: (_err, { taskId }, context) => {
      const ctx = context as
        | { lists: [readonly unknown[], ListTasksResponse | undefined][]; prevTask?: TaskDetail }
        | undefined;
      for (const [key, data] of ctx?.lists ?? []) queryClient.setQueryData(key, data);
      if (ctx?.prevTask) queryClient.setQueryData(taskKey(taskId), ctx.prevTask);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
    },
    // Board/list status changes fail silently otherwise — the optimistic row
    // just snaps back. Surface the standardized error toast (DRD §18.2).
    meta: { errorToast: true },
  });
}
