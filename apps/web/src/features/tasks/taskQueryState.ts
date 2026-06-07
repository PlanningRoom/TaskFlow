import type { DueFilter, TaskPriority, TaskQueryParams, TaskSort, TaskStatus } from './useTasks';

/**
 * URL search-param state for the board + list views, so filter/sort survive a
 * view toggle and are shareable. `validateTaskSearch` is the TanStack Router
 * `validateSearch` for all three project routes; `searchToParams` maps it onto
 * the backend task query.
 */
export interface TaskSearch {
  status?: TaskStatus[];
  assignee?: string[];
  priority?: TaskPriority[];
  label?: string[];
  due?: DueFilter;
  sort?: TaskSort;
  /** Show Cancelled tasks (hidden by default per PRD §6.9). */
  cancelled?: boolean;
}

const STATUSES: TaskStatus[] = ['backlog', 'todo', 'in_progress', 'in_review', 'done', 'cancelled'];
const PRIORITIES: TaskPriority[] = ['none', 'low', 'medium', 'high', 'urgent'];
const DUE_FILTERS: DueFilter[] = ['overdue', 'today', 'this_week', 'no_due_date'];
const SORTS: TaskSort[] = ['created_at', 'priority', 'due_date', 'assignee'];

function strArray(value: unknown): string[] | undefined {
  if (!Array.isArray(value)) return undefined;
  const items = value.filter((v): v is string => typeof v === 'string');
  return items.length ? items : undefined;
}

function enumArray<T extends string>(value: unknown, allowed: T[]): T[] | undefined {
  const items = strArray(value)?.filter((v): v is T => (allowed as string[]).includes(v));
  return items?.length ? items : undefined;
}

function enumValue<T extends string>(value: unknown, allowed: T[]): T | undefined {
  return typeof value === 'string' && (allowed as string[]).includes(value)
    ? (value as T)
    : undefined;
}

export function validateTaskSearch(search: Record<string, unknown>): TaskSearch {
  return {
    status: enumArray(search.status, STATUSES),
    assignee: strArray(search.assignee),
    priority: enumArray(search.priority, PRIORITIES),
    label: strArray(search.label),
    due: enumValue(search.due, DUE_FILTERS),
    sort: enumValue(search.sort, SORTS),
    cancelled: search.cancelled === true ? true : undefined,
  };
}

/** Map URL search state onto the backend `/projects/:id/tasks` query params. */
export function searchToParams(search: TaskSearch): TaskQueryParams {
  return {
    status: search.status,
    assignee: search.assignee,
    priority: search.priority,
    label: search.label,
    due: search.due,
    sort: search.sort,
    include_cancelled: search.cancelled || search.status?.includes('cancelled') || undefined,
  };
}

/** True when any filter (not sort) is active — drives the chip bar visibility. */
export function hasActiveFilters(search: TaskSearch): boolean {
  return Boolean(
    search.status?.length ||
      search.assignee?.length ||
      search.priority?.length ||
      search.label?.length ||
      search.due ||
      search.cancelled,
  );
}
