import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { ChatPanel } from '../src/components/chat/ChatPanel';
import { ThemeProvider } from '../src/context/ThemeContext';

function renderWithProviders() {
  const client = new QueryClient();
  render(
    <QueryClientProvider client={client}>
      <ThemeProvider>
        <BrowserRouter>
          <ChatPanel />
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>,
  );
}

describe('ChatPanel', () => {
  it('renders the legal query entry point', () => {
    renderWithProviders();
    expect(screen.getByText('Legal Query Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask about an Indian legal issue...')).toBeInTheDocument();
  });
});

