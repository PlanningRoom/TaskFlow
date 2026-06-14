import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './Tooltip';

function renderTooltip() {
  return render(
    <TooltipProvider>
      <Tooltip open>
        <TooltipTrigger>Help</TooltipTrigger>
        <TooltipContent>More info</TooltipContent>
      </Tooltip>
    </TooltipProvider>,
  );
}

describe('Tooltip', () => {
  it('renders trigger and content when open', () => {
    const { getByText, getAllByText } = renderTooltip();
    expect(getByText('Help')).toBeInTheDocument();
    // Radix renders the content text in both the visible tooltip and an
    // accessibility mirror, so there is at least one match.
    expect(getAllByText('More info').length).toBeGreaterThan(0);
  });
});
