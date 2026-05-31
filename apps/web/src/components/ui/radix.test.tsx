import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { axe } from '@/test/axe';
import { Checkbox } from './Checkbox';
import { Dialog, DialogContent, DialogDescription, DialogTrigger } from './Dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './DropdownMenu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './Tabs';
import { ToastProvider, useToast } from './Toast';

describe('Dialog', () => {
  it('opens on trigger, shows title, closes on the × button', async () => {
    render(
      <Dialog>
        <DialogTrigger>Open</DialogTrigger>
        <DialogContent title="Create project">
          <DialogDescription>Create a new project.</DialogDescription>
          <p>Body</p>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.queryByText('Create project')).toBeNull();
    await userEvent.click(screen.getByText('Open'));
    expect(screen.getByText('Create project')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Close' }));
    await waitFor(() => expect(screen.queryByText('Create project')).toBeNull());
  });
});

describe('Tabs', () => {
  it('switches panels and is axe-clean', async () => {
    const { container } = render(
      <Tabs defaultValue="a">
        <TabsList>
          <TabsTrigger value="a">Workspace</TabsTrigger>
          <TabsTrigger value="b">Members</TabsTrigger>
        </TabsList>
        <TabsContent value="a">Workspace panel</TabsContent>
        <TabsContent value="b">Members panel</TabsContent>
      </Tabs>,
    );
    expect(screen.getByText('Workspace panel')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('tab', { name: 'Members' }));
    expect(screen.getByText('Members panel')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });
});

describe('Checkbox', () => {
  it('toggles checked state', async () => {
    render(<Checkbox aria-label="Accept" />);
    const box = screen.getByRole('checkbox', { name: 'Accept' });
    expect(box).toHaveAttribute('data-state', 'unchecked');
    await userEvent.click(box);
    expect(box).toHaveAttribute('data-state', 'checked');
  });
});

describe('DropdownMenu', () => {
  it('opens and invokes an item', async () => {
    render(
      <DropdownMenu>
        <DropdownMenuTrigger>Menu</DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem>Edit</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>,
    );
    await userEvent.click(screen.getByText('Menu'));
    expect(await screen.findByText('Edit')).toBeInTheDocument();
  });
});

function ToastButton() {
  const { show } = useToast();
  return (
    <button type="button" onClick={() => show('Task created.')}>
      Create
    </button>
  );
}

describe('Toast', () => {
  it('shows a toast message on demand', async () => {
    render(
      <ToastProvider>
        <ToastButton />
      </ToastProvider>,
    );
    await userEvent.click(screen.getByText('Create'));
    expect(await screen.findByText('Task created.')).toBeInTheDocument();
  });
});
