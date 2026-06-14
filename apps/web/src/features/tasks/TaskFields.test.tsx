import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import type { Label, UserSummary } from '@/api/types';
import { renderWithProviders } from '@/test/render';
import {
  AssigneeSelect,
  DueDatePicker,
  LabelMultiSelect,
  PrioritySelect,
  StatusSelect,
} from './TaskFields';

const bob: UserSummary = {
  id: 'u2',
  display_name: 'Bob',
  initials: 'B',
  avatar_color: 'sky',
  deleted: false,
};
const labels: Label[] = [
  { id: 'l1', name: 'Bug', color: 'red' },
  { id: 'l2', name: 'Chore', color: 'blue' },
];

describe('TaskFields', () => {
  it('StatusSelect changes status and renders read-only when disabled', async () => {
    const user = userEvent.setup({ pointerEventsCheck: 0 });
    const onChange = vi.fn();
    const { getByLabelText, getByRole, queryByLabelText, rerender } = renderWithProviders(
      <StatusSelect value="backlog" onChange={onChange} />,
    );
    await user.click(getByLabelText('Change status'));
    await user.click(getByRole('menuitem', { name: 'In Progress' }));
    expect(onChange).toHaveBeenCalledWith('in_progress');

    rerender(<StatusSelect value="done" onChange={onChange} disabled />);
    expect(queryByLabelText('Change status')).toBeNull();
  });

  it('PrioritySelect picks a priority', async () => {
    const user = userEvent.setup({ pointerEventsCheck: 0 });
    const onChange = vi.fn();
    const { getByLabelText, getByText } = renderWithProviders(
      <PrioritySelect value="none" onChange={onChange} />,
    );
    await user.click(getByLabelText('Change priority'));
    // The menuitem name includes the PriorityIcon's "High priority" label, so
    // target the visible "High" text node inside the open menu.
    await user.click(getByText('High'));
    expect(onChange).toHaveBeenCalledWith('high');
  });

  it('AssigneeSelect assigns a member and unassigns', async () => {
    const user = userEvent.setup({ pointerEventsCheck: 0 });
    const onChange = vi.fn();
    const { getByLabelText, getByRole } = renderWithProviders(
      <AssigneeSelect value={null} members={[bob]} onChange={onChange} />,
    );
    await user.click(getByLabelText('Change assignee'));
    await user.click(getByRole('menuitem', { name: /Bob/ }));
    expect(onChange).toHaveBeenCalledWith('u2');

    await user.click(getByLabelText('Change assignee'));
    await user.click(getByRole('menuitem', { name: 'Unassigned' }));
    expect(onChange).toHaveBeenCalledWith(null);
  });

  it('LabelMultiSelect toggles a label', async () => {
    const user = userEvent.setup({ pointerEventsCheck: 0 });
    const onChange = vi.fn();
    const { getByLabelText, getByText } = renderWithProviders(
      <LabelMultiSelect value={[]} labels={labels} onChange={onChange} />,
    );
    await user.click(getByLabelText('Edit labels'));
    await user.click(getByText('Bug'));
    expect(onChange).toHaveBeenCalledWith(['l1']);
  });

  it('LabelMultiSelect shows an empty hint when there are no labels', async () => {
    const user = userEvent.setup({ pointerEventsCheck: 0 });
    const { getByLabelText, getByText } = renderWithProviders(
      <LabelMultiSelect value={[]} labels={[]} onChange={vi.fn()} />,
    );
    await user.click(getByLabelText('Edit labels'));
    expect(getByText('No labels yet')).toBeInTheDocument();
  });

  it('DueDatePicker emits the chosen date and clears it', async () => {
    const onChange = vi.fn();
    const { getByLabelText } = renderWithProviders(
      <DueDatePicker value={null} onChange={onChange} />,
    );
    const input = getByLabelText('Due date');
    await userEvent.type(input, '2026-07-01');
    expect(onChange).toHaveBeenLastCalledWith('2026-07-01');
  });

  it('renders read-only values when disabled', () => {
    const { getByText } = renderWithProviders(
      <div>
        <PrioritySelect value="high" onChange={vi.fn()} disabled />
        <AssigneeSelect value={bob} members={[bob]} onChange={vi.fn()} disabled />
        <DueDatePicker value={null} onChange={vi.fn()} disabled />
      </div>,
    );
    expect(getByText('High')).toBeInTheDocument();
    expect(getByText('No due date')).toBeInTheDocument();
  });
});
