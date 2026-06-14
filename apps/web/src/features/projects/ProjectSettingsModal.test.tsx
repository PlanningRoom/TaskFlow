import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { Button } from '@/components/ui';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { ProjectSettingsModal } from './ProjectSettingsModal';

const owner = {
  id: 'u1',
  email: 'o@aurora.example.com',
  display_name: 'Olivia',
  initials: 'O',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

const members = [
  {
    id: 'u2',
    display_name: 'Bob',
    email: 'bob@aurora.example.com',
    initials: 'B',
    avatar_color: 'sky',
    role: 'member',
    joined_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'u3',
    display_name: 'Vic',
    email: 'vic@aurora.example.com',
    initials: 'V',
    avatar_color: 'rose',
    role: 'viewer',
    joined_at: '2026-01-01T00:00:00Z',
  },
];

function mockApi() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(owner);
    if (path === '/projects/p1')
      return Promise.resolve({
        id: 'p1',
        name: 'Website Redesign',
        description: 'Marketing site',
        color: '#0d9488',
      });
    if (path === '/projects/p1/access')
      return Promise.resolve({
        members: [{ user: { id: 'u2', display_name: 'Bob', initials: 'B', avatar_color: 'sky' } }],
      });
    if (path === '/workspaces/me/members') return Promise.resolve({ members });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

function open() {
  return renderWithProviders(
    <ProjectSettingsModal projectId="p1" trigger={<Button>Project settings</Button>} />,
  );
}

afterEach(() => vi.restoreAllMocks());

describe('ProjectSettingsModal', () => {
  it('opens and prefills the Details tab with the project name', async () => {
    mockApi();
    const user = userEvent.setup();
    const { getByRole, findByDisplayValue } = open();
    await user.click(getByRole('button', { name: 'Project settings' }));
    expect(await findByDisplayValue('Website Redesign')).toBeInTheDocument();
  });

  it('lists granted members on the Access tab', async () => {
    mockApi();
    const user = userEvent.setup();
    const { getByRole, findByRole, getByText } = open();
    await user.click(getByRole('button', { name: 'Project settings' }));
    await user.click(await findByRole('tab', { name: 'Access' }));
    expect(getByText('Bob')).toBeInTheDocument();
    // The viewer not yet granted is an add-candidate, not in the granted list.
    expect(getByRole('button', { name: /Add member/ })).toBeEnabled();
  });

  it('has no axe violations when open', async () => {
    mockApi();
    const user = userEvent.setup();
    const { getByRole, findByDisplayValue, baseElement } = open();
    await user.click(getByRole('button', { name: 'Project settings' }));
    await findByDisplayValue('Website Redesign');
    expect(await axe(baseElement)).toHaveNoViolations();
  });
});
