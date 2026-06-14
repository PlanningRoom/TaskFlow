import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { Button } from '@/components/ui';
import { renderWithProviders } from '@/test/render';
import { CreateTaskModal } from './CreateTaskModal';

const owner = {
  id: 'u1',
  email: 'o@aurora.example.com',
  display_name: 'Olivia',
  initials: 'O',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

function mockApi() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(owner);
    if (path === '/projects/p1/access') return Promise.resolve({ members: [] });
    if (path === '/labels') return Promise.resolve({ labels: [] });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('CreateTaskModal', () => {
  it('submits a new task with the title and chosen priority', async () => {
    mockApi();
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ id: 't9', title: 'Ship it' });
    const user = userEvent.setup({ pointerEventsCheck: 0 });

    const { getByRole, getByText, findByLabelText, findByText } = renderWithProviders(
      <CreateTaskModal projectId="p1" trigger={<Button>New task</Button>} />,
    );
    await user.click(getByRole('button', { name: 'New task' }));
    await user.type(await findByLabelText('Title'), 'Ship it');

    // Change priority via the controlled select (menuitem name carries the
    // PriorityIcon label, so click the visible "High" text).
    await user.click(getByRole('button', { name: 'Change priority' }));
    await user.click(getByText('High'));

    await user.click(getByRole('button', { name: 'Create task' }));

    expect(post).toHaveBeenCalledWith(
      '/projects/p1/tasks',
      expect.objectContaining({ title: 'Ship it', priority: 'high' }),
    );
    expect(await findByText('Task created.')).toBeInTheDocument();
  });

  it('blocks submit when the title is empty', async () => {
    mockApi();
    const post = vi.spyOn(apiClient, 'post');
    const user = userEvent.setup({ pointerEventsCheck: 0 });

    const { getByRole } = renderWithProviders(
      <CreateTaskModal projectId="p1" trigger={<Button>New task</Button>} />,
    );
    await user.click(getByRole('button', { name: 'New task' }));
    await user.click(getByRole('button', { name: 'Create task' }));

    expect(post).not.toHaveBeenCalled();
  });
});
