import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import type { ActivityEvent } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { ProjectActivityPanel } from './ProjectActivityPanel';

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}));

const event: ActivityEvent = {
  id: 'a1',
  event_type: 'task.created',
  actor: {
    id: 'u1',
    display_name: 'Olivia',
    initials: 'O',
    avatar_color: 'indigo',
    deleted: false,
  },
  subject_type: 'task',
  subject_id: 't1',
  detail: 'Fix the login bug',
  project: { id: 'p1', name: 'Website' },
  metadata: {},
  created_at: '2026-07-01T10:00:00Z',
};

afterEach(() => vi.restoreAllMocks());

describe('ProjectActivityPanel', () => {
  it('fetches project-scoped activity and renders rows, with no axe violations', async () => {
    const get = vi.spyOn(apiClient, 'get').mockResolvedValue({ events: [event] });
    const { container, findByText, getByRole } = renderWithProviders(
      <ProjectActivityPanel projectId="p1" onClose={vi.fn()} />,
    );
    expect(getByRole('dialog', { name: 'Project activity' })).toBeInTheDocument();
    expect(await findByText('Olivia')).toBeInTheDocument();
    expect(await findByText('Fix the login bug')).toBeInTheDocument();
    expect(get).toHaveBeenCalledWith('/activity', { query: { project_id: 'p1' } });
    expect(await axe(container)).toHaveNoViolations();
  });

  it('shows the empty state and closes via × and Escape', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ events: [] });
    const onClose = vi.fn();
    const { findByText, getByLabelText } = renderWithProviders(
      <ProjectActivityPanel projectId="p1" onClose={onClose} />,
    );
    expect(await findByText('No activity in this project yet.')).toBeInTheDocument();
    await userEvent.click(getByLabelText('Close activity panel'));
    expect(onClose).toHaveBeenCalledTimes(1);
    await userEvent.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledTimes(2);
  });
});
