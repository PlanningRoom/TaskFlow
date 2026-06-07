import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { ToastProvider } from '@/components/ui';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { CreateProjectModal } from './CreateProjectModal';

const { mockNavigate } = vi.hoisted(() => ({ mockNavigate: vi.fn() }));
vi.mock('@tanstack/react-router', () => ({ useNavigate: () => mockNavigate }));

afterEach(() => vi.restoreAllMocks());

function render() {
  return renderWithProviders(
    <ToastProvider>
      <CreateProjectModal
        trigger={
          <button type="button" aria-label="New project">
            +
          </button>
        }
      />
    </ToastProvider>,
  );
}

describe('CreateProjectModal', () => {
  it('opens from its trigger with no axe violations', async () => {
    const { getByRole } = render();
    await userEvent.click(getByRole('button', { name: 'New project' }));
    const dialog = await waitFor(() => getByRole('dialog'));
    // Scope axe to the dialog subtree: running it on document.body would trip
    // page-level rules (no h1 / region) that don't apply to a modal fragment.
    expect(await axe(dialog)).toHaveNoViolations();
  });

  it('validates that a project name is required', async () => {
    const post = vi.spyOn(apiClient, 'post');
    const { getByRole, findByText } = render();
    await userEvent.click(getByRole('button', { name: 'New project' }));
    await userEvent.click(getByRole('button', { name: 'Create project' }));
    expect(await findByText('Project name is required')).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it('creates a project and navigates to its board', async () => {
    const post = vi
      .spyOn(apiClient, 'post')
      .mockResolvedValue({ id: 'p9', name: 'Launch Plan', description: null });
    const { getByRole, getByLabelText } = render();
    await userEvent.click(getByRole('button', { name: 'New project' }));
    await userEvent.type(getByLabelText('Project name'), 'Launch Plan');
    await userEvent.click(getByRole('button', { name: 'Create project' }));
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/projects', {
        name: 'Launch Plan',
        description: null,
      }),
    );
    expect(mockNavigate).toHaveBeenCalledWith({
      to: '/projects/$projectId/board',
      params: { projectId: 'p9' },
    });
  });
});
