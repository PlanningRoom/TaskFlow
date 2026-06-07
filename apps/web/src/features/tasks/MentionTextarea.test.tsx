import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import type { UserSummary } from '@/api/types';
import { renderWithProviders } from '@/test/render';
import { MentionTextarea, mentionHandle } from './MentionTextarea';

const members: UserSummary[] = [
  {
    id: 'u1',
    display_name: 'Aurora Owner',
    initials: 'AO',
    avatar_color: 'indigo',
    deleted: false,
  },
  { id: 'u2', display_name: 'Bob Builder', initials: 'BB', avatar_color: 'sky', deleted: false },
];

function Harness() {
  const [value, setValue] = useState('');
  return (
    <>
      <MentionTextarea id="c" value={value} onChange={setValue} members={members} />
      <output data-testid="value">{value}</output>
    </>
  );
}

describe('mentionHandle', () => {
  it('lowercases and hyphenates the display name', () => {
    expect(mentionHandle('Aurora Owner')).toBe('aurora-owner');
    expect(mentionHandle(null)).toBe('');
  });
});

describe('MentionTextarea', () => {
  it('opens a filtered member dropdown after typing @', async () => {
    const { getByRole, findByText, queryByText } = renderWithProviders(<Harness />);
    await userEvent.type(getByRole('textbox'), 'hi @aur');
    expect(await findByText('Aurora Owner')).toBeInTheDocument();
    expect(queryByText('Bob Builder')).toBeNull();
  });

  it('inserts the backend handle on selection', async () => {
    const { getByRole, findByText, getByTestId } = renderWithProviders(<Harness />);
    await userEvent.type(getByRole('textbox'), '@aur');
    await userEvent.click(await findByText('Aurora Owner'));
    expect(getByTestId('value').textContent).toBe('@aurora-owner ');
  });

  it('supports keyboard selection with arrows and Enter', async () => {
    const { getByRole, getByTestId, findByText } = renderWithProviders(<Harness />);
    const box = getByRole('textbox');
    await userEvent.type(box, '@b');
    await findByText('Bob Builder');
    await userEvent.keyboard('{Enter}');
    expect(getByTestId('value').textContent).toBe('@bob-builder ');
  });
});
