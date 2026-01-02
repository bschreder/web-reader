import React from 'react';
import { describe, expect, it } from 'vitest';
import { cleanup, render } from 'vitest-browser-react';
import AnswerDisplay from '../../../src/components/AnswerDisplay';

describe('AnswerDisplay (browser)', () => {
  it('renders answer and citations', async () => {
    const screen = await render(
      <AnswerDisplay
        answer={'Line 1\nLine 2'}
        citations={[{ title: 'Example', url: 'https://example.com' }]}
        confidence={0.9}
      />
    );

    await expect.element(screen.getByText('Citations')).toBeVisible();
    await expect.element(screen.getByText('Line 1')).toBeVisible();
    await cleanup();
  });
});
