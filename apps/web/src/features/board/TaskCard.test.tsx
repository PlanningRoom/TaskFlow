import { DndContext } from '@dnd-kit/core';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import type { TaskSummary } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { TaskCard } from './TaskCard';

const baseTask: TaskSummary = {
  id: 't1',
  title: 'Fix the login bug',
  status: 'in_progress',
  priority: 'high',
  due_date: null,
  assignee: null,
  labels: [],
  comment_count: 0,
  project: { id: 'p1', name: 'Website Redesign' },
};

function renderCard(task: TaskSummary, { canDrag = true, onOpen = vi.fn() } = {}) {
  return {
    onOpen,
    ...renderWithProviders(
      <DndContext>
        <TaskCard task={task} canDrag={canDrag} onOpen={onOpen} />
      </DndContext>,
    ),
  };
}

describe('TaskCard', () => {
  it('opens the task on click', async () => {
    const user = userEvent.setup();
    const { onOpen, getByRole } = renderCard(baseTask, { canDrag: false });
    await user.click(getByRole('button', { name: /Fix the login bug/ }));
    expect(onOpen).toHaveBeenCalledOnce();
  });

  it('renders up to three labels plus an overflow indicator', () => {
    const labels = Array.from({ length: 5 }, (_, i) => ({
      id: `l${i}`,
      name: `Label ${i}`,
      color: 'blue' as const,
    }));
    const { getByText, queryByText } = renderCard({ ...baseTask, labels });
    expect(getByText('Label 0')).toBeInTheDocument();
    expect(getByText('Label 2')).toBeInTheDocument();
    expect(queryByText('Label 3')).toBeNull();
    expect(getByText('+2')).toBeInTheDocument();
  });

  it('shows comment count and assignee avatar when present', () => {
    const { getByText, getByLabelText } = renderCard({
      ...baseTask,
      comment_count: 4,
      assignee: {
        id: 'u2',
        display_name: 'Bob',
        initials: 'B',
        avatar_color: 'sky',
        deleted: false,
      },
    });
    expect(getByText('4')).toBeInTheDocument();
    expect(getByLabelText('B')).toBeInTheDocument();
  });

  it('has no axe violations', async () => {
    const { container } = renderCard(baseTask);
    expect(await axe(container)).toHaveNoViolations();
  });
});
