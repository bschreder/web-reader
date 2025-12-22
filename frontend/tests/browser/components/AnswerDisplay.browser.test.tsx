import React from 'react';
import { describe, expect, it } from 'vitest';
import { createRoot } from 'react-dom/client';
import AnswerDisplay from '../../../src/components/AnswerDisplay';

describe('AnswerDisplay (browser)', () => {
  it('renders answer and citations', () => {
    const el = document.createElement('div');
    document.body.appendChild(el);
    const root = createRoot(el);

    root.render(
      <AnswerDisplay
        answer={'Line 1\nLine 2'}
        citations={[{ title: 'Example', url: 'https://example.com' }]}
        confidence={0.9}
      />
    );

    expect(el.textContent).toContain('Citations');
    expect(el.textContent).toContain('Line 1');
    root.unmount();
    el.remove();
  });
});
