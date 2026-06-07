import { useIntl } from 'react-intl';
import type { CurrentUser } from '@/api/types';
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  STATUS_LABELS,
} from '@/components/ui';
import {
  Check,
  ChevronDown,
  Filter,
  LayoutGrid,
  List,
  Plus,
  Settings,
} from '@/components/ui/icons';
import { ProjectSettingsModal } from '@/features/projects/ProjectSettingsModal';
import { useLabels } from '@/features/settings/useLabels';
import { useMembers } from '@/features/settings/useMembers';
import { cn } from '@/lib/cn';
import type { ProjectViewKind } from '@/lib/projectView';
import { CreateTaskModal } from './CreateTaskModal';
import { PRIORITY_LABELS } from './TaskFields';
import { hasActiveFilters, type TaskSearch } from './taskQueryState';
import type { DueFilter, TaskPriority, TaskSort, TaskStatus } from './useTasks';

/**
 * Project sub-navigation bar (DRD §8.4 / screen inventory §3.5): view toggle,
 * Filter popover, active-filter chips + Clear all, Sort dropdown, project
 * settings (Owner/Admin), and the role-gated "+ Create task" button.
 */
const SORT_LABELS: Record<TaskSort, string> = {
  created_at: 'Creation date',
  priority: 'Priority',
  due_date: 'Due date',
  assignee: 'Assignee',
};
const STATUS_ORDER: TaskStatus[] = ['backlog', 'todo', 'in_progress', 'in_review', 'done'];
const PRIORITY_ORDER: TaskPriority[] = ['urgent', 'high', 'medium', 'low', 'none'];
const DUE_LABELS: Record<DueFilter, string> = {
  overdue: 'Overdue',
  today: 'Due today',
  this_week: 'Due this week',
  no_due_date: 'No due date',
};

export function ProjectSubNav({
  projectId,
  view,
  search,
  role,
  onViewChange,
  onSearchChange,
}: {
  projectId: string;
  view: ProjectViewKind;
  search: TaskSearch;
  role: CurrentUser['role'];
  onViewChange: (view: ProjectViewKind) => void;
  onSearchChange: (search: TaskSearch) => void;
}) {
  const intl = useIntl();
  const canEdit = role !== 'viewer';
  const canManage = role === 'owner' || role === 'admin';

  return (
    <div className="border-b border-border bg-bg-card">
      <div className="flex items-center gap-3 px-6 py-2.5">
        <ViewToggle view={view} onChange={onViewChange} />
        <span className="h-5 w-px bg-border" aria-hidden />
        <FilterPopover search={search} onChange={onSearchChange} />
        <SortDropdown
          value={search.sort ?? 'created_at'}
          onChange={(sort) => onSearchChange({ ...search, sort })}
        />
        <div className="ms-auto flex items-center gap-2">
          {canManage ? (
            <ProjectSettingsModal
              projectId={projectId}
              trigger={
                <button
                  type="button"
                  className="rounded-sm p-1.5 text-text-tertiary hover:bg-bg-hover hover:text-text-primary"
                  aria-label={intl.formatMessage({ id: 'project.settings.title' })}
                >
                  <Settings size={18} strokeWidth={1.75} />
                </button>
              }
            />
          ) : null}
          {canEdit ? (
            <CreateTaskModal
              projectId={projectId}
              trigger={
                <Button size="sm">
                  <Plus size={16} strokeWidth={1.75} />
                  {intl.formatMessage({ id: 'task.create.button' })}
                </Button>
              }
            />
          ) : null}
        </div>
      </div>
      {hasActiveFilters(search) ? <FilterChips search={search} onChange={onSearchChange} /> : null}
    </div>
  );
}

function ViewToggle({
  view,
  onChange,
}: {
  view: ProjectViewKind;
  onChange: (view: ProjectViewKind) => void;
}) {
  const item = (kind: ProjectViewKind, label: string, icon: React.ReactNode) => (
    <button
      type="button"
      onClick={() => onChange(kind)}
      aria-pressed={view === kind}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-sm px-2.5 py-1 text-[13px]',
        view === kind ? 'bg-primary text-white' : 'text-text-secondary hover:bg-bg-hover',
      )}
    >
      {icon}
      {label}
    </button>
  );
  return (
    <div className="inline-flex rounded-sm border border-border p-0.5">
      {item('board', 'Board', <LayoutGrid size={15} strokeWidth={1.75} />)}
      {item('list', 'List', <List size={15} strokeWidth={1.75} />)}
    </div>
  );
}

function SortDropdown({
  value,
  onChange,
}: {
  value: TaskSort;
  onChange: (sort: TaskSort) => void;
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="inline-flex items-center gap-1.5 rounded-sm border border-border px-2.5 py-1.5 text-[13px] text-text-secondary hover:bg-bg-hover">
        Sort: {SORT_LABELS[value]}
        <ChevronDown size={14} />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {(Object.keys(SORT_LABELS) as TaskSort[]).map((sort) => (
          <DropdownMenuItem key={sort} onSelect={() => onChange(sort)}>
            <span className="flex w-4 justify-center">
              {value === sort ? <Check size={14} className="text-primary" /> : null}
            </span>
            {SORT_LABELS[sort]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function FilterPopover({
  search,
  onChange,
}: {
  search: TaskSearch;
  onChange: (search: TaskSearch) => void;
}) {
  const { data: memberData } = useMembers();
  const { data: labelData } = useLabels();
  const members = memberData?.members ?? [];
  const labels = labelData?.labels ?? [];

  function toggle<T>(list: T[] | undefined, item: T): T[] | undefined {
    const next = (list ?? []).includes(item)
      ? (list ?? []).filter((v) => v !== item)
      : [...(list ?? []), item];
    return next.length ? next : undefined;
  }

  const keepOpen = (e: Event) => e.preventDefault();
  const row = (active: boolean, label: React.ReactNode, onSelect: () => void, key: string) => (
    <DropdownMenuItem
      key={key}
      onSelect={(e) => {
        keepOpen(e);
        onSelect();
      }}
    >
      <span className="flex w-4 justify-center">
        {active ? <Check size={14} className="text-primary" /> : null}
      </span>
      {label}
    </DropdownMenuItem>
  );

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="inline-flex items-center gap-1.5 rounded-sm border border-border px-2.5 py-1.5 text-[13px] text-text-secondary hover:bg-bg-hover">
        <Filter size={14} />
        Filter
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="max-h-[70vh] overflow-y-auto">
        <div className="px-2 py-1 text-[11px] font-semibold uppercase text-text-tertiary">
          Status
        </div>
        {STATUS_ORDER.map((s) =>
          row(
            search.status?.includes(s) ?? false,
            STATUS_LABELS[s],
            () => onChange({ ...search, status: toggle(search.status, s) }),
            `st-${s}`,
          ),
        )}
        <DropdownMenuSeparator />
        <div className="px-2 py-1 text-[11px] font-semibold uppercase text-text-tertiary">
          Priority
        </div>
        {PRIORITY_ORDER.map((p) =>
          row(
            search.priority?.includes(p) ?? false,
            PRIORITY_LABELS[p],
            () => onChange({ ...search, priority: toggle(search.priority, p) }),
            `pr-${p}`,
          ),
        )}
        <DropdownMenuSeparator />
        <div className="px-2 py-1 text-[11px] font-semibold uppercase text-text-tertiary">Due</div>
        {(Object.keys(DUE_LABELS) as DueFilter[]).map((d) =>
          row(
            search.due === d,
            DUE_LABELS[d],
            () => onChange({ ...search, due: search.due === d ? undefined : d }),
            `due-${d}`,
          ),
        )}
        {members.length ? (
          <>
            <DropdownMenuSeparator />
            <div className="px-2 py-1 text-[11px] font-semibold uppercase text-text-tertiary">
              Assignee
            </div>
            {members.map((m) =>
              row(
                search.assignee?.includes(m.id) ?? false,
                m.display_name ?? m.email,
                () => onChange({ ...search, assignee: toggle(search.assignee, m.id) }),
                `as-${m.id}`,
              ),
            )}
          </>
        ) : null}
        {labels.length ? (
          <>
            <DropdownMenuSeparator />
            <div className="px-2 py-1 text-[11px] font-semibold uppercase text-text-tertiary">
              Labels
            </div>
            {labels.map((l) =>
              row(
                search.label?.includes(l.id) ?? false,
                l.name,
                () => onChange({ ...search, label: toggle(search.label, l.id) }),
                `lb-${l.id}`,
              ),
            )}
          </>
        ) : null}
        <DropdownMenuSeparator />
        {row(
          search.cancelled ?? false,
          'Show cancelled',
          () => onChange({ ...search, cancelled: search.cancelled ? undefined : true }),
          'cancelled',
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function FilterChips({
  search,
  onChange,
}: {
  search: TaskSearch;
  onChange: (search: TaskSearch) => void;
}) {
  const { data: memberData } = useMembers();
  const { data: labelData } = useLabels();
  const memberName = (id: string) =>
    memberData?.members.find((m) => m.id === id)?.display_name ?? 'Member';
  const labelName = (id: string) => labelData?.labels.find((l) => l.id === id)?.name ?? 'Label';

  const chips: { key: string; label: string; remove: () => void }[] = [];
  for (const s of search.status ?? [])
    chips.push({
      key: `st-${s}`,
      label: STATUS_LABELS[s],
      remove: () => onChange({ ...search, status: drop(search.status, s) }),
    });
  for (const p of search.priority ?? [])
    chips.push({
      key: `pr-${p}`,
      label: PRIORITY_LABELS[p],
      remove: () => onChange({ ...search, priority: drop(search.priority, p) }),
    });
  if (search.due)
    chips.push({
      key: 'due',
      label: DUE_LABELS[search.due],
      remove: () => onChange({ ...search, due: undefined }),
    });
  for (const a of search.assignee ?? [])
    chips.push({
      key: `as-${a}`,
      label: memberName(a),
      remove: () => onChange({ ...search, assignee: drop(search.assignee, a) }),
    });
  for (const l of search.label ?? [])
    chips.push({
      key: `lb-${l}`,
      label: labelName(l),
      remove: () => onChange({ ...search, label: drop(search.label, l) }),
    });
  if (search.cancelled)
    chips.push({
      key: 'cancelled',
      label: 'Cancelled',
      remove: () => onChange({ ...search, cancelled: undefined }),
    });

  return (
    <div className="flex flex-wrap items-center gap-2 px-6 pb-2.5">
      {chips.map((chip) => (
        <span
          key={chip.key}
          className="inline-flex items-center gap-1 rounded-chip bg-primary-light px-2 py-0.5 text-[11px] text-primary-text"
        >
          {chip.label}
          <button
            type="button"
            onClick={chip.remove}
            aria-label={`Remove ${chip.label} filter`}
            className="text-primary-text/70 hover:text-primary-text"
          >
            ×
          </button>
        </span>
      ))}
      <button
        type="button"
        onClick={() => onChange({ sort: search.sort })}
        className="text-[11px] text-text-secondary underline hover:text-text-primary"
      >
        Clear all
      </button>
    </div>
  );
}

function drop<T>(list: T[] | undefined, item: T): T[] | undefined {
  const next = (list ?? []).filter((v) => v !== item);
  return next.length ? next : undefined;
}
