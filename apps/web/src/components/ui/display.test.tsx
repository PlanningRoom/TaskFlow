import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { axe } from '@/test/axe';
import { DueDate, formatDueDate } from './DueDate';
import { LabelChip, LabelOverflow } from './LabelChip';
import { PriorityIcon } from './PriorityIcon';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  it('renders the label for each status with no axe violations', async () => {
    const { container, getByText } = render(
      <div>
        <StatusBadge status="backlog" />
        <StatusBadge status="todo" />
        <StatusBadge status="in_progress" />
        <StatusBadge status="in_review" />
        <StatusBadge status="done" />
        <StatusBadge status="cancelled" />
      </div>,
    );
    expect(getByText('In Progress')).toBeInTheDocument();
    expect(getByText('In Review')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});

describe('LabelChip', () => {
  it('renders colored chips and overflow with no axe violations', async () => {
    const { container, getByText, queryByText } = render(
      <div>
        <LabelChip name="Design" color="blue" />
        <LabelChip name="Bug" color="red" />
        <LabelOverflow count={2} />
        <LabelOverflow count={0} />
      </div>,
    );
    expect(getByText('Design')).toHaveClass('bg-label-blue');
    expect(getByText('+2')).toBeInTheDocument();
    expect(queryByText('+0')).toBeNull();
    expect(await axe(container)).toHaveNoViolations();
  });
});

describe('PriorityIcon', () => {
  it('renders a labeled glyph per priority and nothing for none', async () => {
    const { container, queryByRole, getByLabelText } = render(
      <div>
        <PriorityIcon priority="urgent" />
        <PriorityIcon priority="low" />
      </div>,
    );
    expect(getByLabelText('Urgent priority')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();

    const none = render(<PriorityIcon priority="none" />);
    expect(none.container).toBeEmptyDOMElement();
    expect(queryByRole).toBeDefined();
  });
});

describe('DueDate', () => {
  const now = new Date(2026, 3, 14); // Apr 14 2026

  it('formats same-year vs other-year', () => {
    expect(formatDueDate(new Date(2026, 3, 15), now)).toBe('Apr 15');
    expect(formatDueDate(new Date(2025, 3, 15), now)).toBe('Apr 15, 2025');
  });

  it('flags overdue and approaching', () => {
    const overdue = render(<DueDate date="2026-04-10" now={now} />);
    expect(overdue.getByText('Apr 10')).toHaveClass('text-semantic-error');

    const approaching = render(<DueDate date="2026-04-15" now={now} />);
    expect(approaching.getByText('Apr 15')).toHaveClass('text-semantic-warning');

    const normal = render(<DueDate date="2026-05-30" now={now} />);
    expect(normal.getByText('May 30')).not.toHaveClass('text-semantic-error');
  });

  it('renders nothing when null', () => {
    const { container } = render(<DueDate date={null} />);
    expect(container).toBeEmptyDOMElement();
  });
});
