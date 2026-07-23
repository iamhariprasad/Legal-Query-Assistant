import { FormEvent, useCallback, useEffect, useRef, useState } from 'react';
import {
  BookOpen,
  Check,
  ChevronDown,
  Copy,
  RefreshCw,
  Send,
  ShieldAlert,
  ThumbsDown,
  ThumbsUp,
  Trash2,
} from 'lucide-react';
import { useChatMutation, useSubmitFeedback } from '../../api/hooks';
import type { ChatResponse } from '../../types/api';
import { useAuth } from '../../context/AuthContext';
import { AuthPanel } from '../common/AuthPanel';
import { ConfidenceMeter } from '../common/ConfidenceMeter';
import { IconButton } from '../common/IconButton';
import { CitationCards } from './CitationCards';
import { MarkdownMessage } from './MarkdownMessage';
import { SourceDrawer } from './SourceDrawer';
import { TypingAnimation } from './TypingAnimation';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: ChatResponse;
  feedback?: { rating: number };
}

const PROGRESS_STATES = [
  'Searching Indian Kanoon...',
  'Retrieving relevant documents...',
  'Reranking results...',
  'Generating answer...',
  'Verifying citations...',
  'Applying guardrails...',
] as const;

export function ChatPanel() {
  // === ALL HOOKS FIRST — always called, same order every render ===
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerCitations, setDrawerCitations] = useState<ChatResponse['citations']>([]);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [progressIndex, setProgressIndex] = useState(0);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [timedOut, setTimedOut] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const chat = useChatMutation();
  const feedbackMutation = useSubmitFeedback();
  const { user, isLoading: authLoading } = useAuth();

  const scrollToBottom = useCallback((force = false) => {
    if (force && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      return;
    }
    const container = containerRef.current;
    if (container) {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      if (isNearBottom) {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, []);

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom(true);
  }, [messages.length, scrollToBottom]);

  // Progress animation during pending state
  useEffect(() => {
    if (chat.isPending) {
      progressIntervalRef.current = setInterval(() => {
        setProgressIndex((prev) => (prev + 1) % PROGRESS_STATES.length);
      }, 4000);
    } else {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setProgressIndex(0);
    }
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, [chat.isPending]);

  // Timeout tracking
  useEffect(() => {
    if (chat.isPending) {
      const timeout = setTimeout(() => setTimedOut(true), 90_000);
      return () => clearTimeout(timeout);
    }
    setTimedOut(false);
  }, [chat.isPending]);

  // === EARLY RETURNS — after all hooks ===
  if (authLoading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <div className="flex items-center gap-2 text-slate-500">
          <TypingAnimation />
          <span className="text-sm">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-start justify-center pt-12">
        <AuthPanel />
      </div>
    );
  }

  // === EVENT HANDLERS ===
  function handleScroll() {
    const container = containerRef.current;
    if (container) {
      const { scrollTop, scrollHeight, clientHeight } = container;
      setShowScrollButton(scrollHeight - scrollTop - clientHeight > 200);
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || chat.isPending) {
      return;
    }
    setError(null);
    setQuery('');
    const messageId = `msg-${Date.now()}`;
    setMessages((current) => [...current, { id: messageId, role: 'user', content: trimmed }]);
    try {
      const response = await chat.mutateAsync(trimmed);
      setMessages((current) => [
        ...current,
        {
          id: response.id || `resp-${Date.now()}`,
          role: 'assistant',
          content: response.answer,
          response,
        },
      ]);
      scrollToBottom(true);
    } catch (err) {
      const errorMessage =
        (err as { response?: { data?: { message?: string } } })?.response?.data?.message ||
        'The request failed. The backend may be unavailable or your session may have expired.';
      setError(errorMessage);
      setMessages((current) => current.filter((m) => m.id !== messageId));
    }
  }

  function handleRetry(message: Message) {
    if (message.role !== 'user') return;
    setError(null);
    setQuery(message.content);
    setMessages((current) => current.filter((m) => m.id !== message.id));
  }

  function handleCopy(content: string, id: string) {
    navigator.clipboard.writeText(content).then(() => {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    });
  }

  function handleClearChat() {
    setMessages([]);
    setError(null);
    chat.reset();
  }

  function handleOpenSources(citations: ChatResponse['citations']) {
    setDrawerCitations(citations);
    setDrawerOpen(true);
  }

  async function handleFeedback(chatId: string, rating: number) {
    try {
      await feedbackMutation.mutateAsync({ chat_id: chatId, rating });
      setMessages((current) =>
        current.map((m) =>
          m.id === chatId ? { ...m, feedback: { rating } } : m,
        ),
      );
    } catch {
      // Silently fail - feedback is non-critical
    }
  }

  // === MAIN RENDER ===
  return (
    <div className="flex h-full min-h-[calc(100vh-4rem)] flex-col">
      {/* Messages area */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 py-6"
      >
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          {/* Welcome message */}
          {messages.length === 0 && !chat.isPending && (
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-panel dark:border-slate-700 dark:bg-slate-900">
              <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                Legal Query Assistant
              </h1>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Ask an Indian legal research question. Answers are citation-grounded and refused when evidence is weak.
                Start with questions about bail, custody, IPC sections, or constitutional law.
              </p>
              <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                Signed in as{' '}
                <span className="font-medium text-slate-700 dark:text-slate-200">{user.email}</span>
                {user.role === 'admin' && (
                  <span className="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-100">
                    Admin
                  </span>
                )}
              </p>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm shadow-panel dark:border-rose-900 dark:bg-rose-950">
              <ShieldAlert size={18} className="mt-0.5 shrink-0 text-rose-600 dark:text-rose-400" />
              <div>
                <p className="font-medium text-rose-800 dark:text-rose-200">Error</p>
                <p className="mt-1 text-rose-700 dark:text-rose-300">{error}</p>
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((message, index) => (
            <div
              key={`${message.id}-${index}`}
              className={`rounded-xl border p-5 shadow-panel ${
                message.role === 'user'
                  ? 'border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/20'
                  : 'border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900'
              }`}
            >
              <div className="mb-3 flex items-center justify-between gap-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  {message.role === 'user' ? 'You' : 'Assistant'}
                </span>
                {message.response && (
                  <div className="flex items-center gap-2">
                    {message.response.refused && (
                      <span className="flex items-center gap-1 rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-100">
                        <ShieldAlert size={14} />
                        Refused
                      </span>
                    )}
                    <ConfidenceMeter value={message.response.confidence} />
                    <div className="flex gap-1">
                      <IconButton
                        label="View authorities"
                        icon={BookOpen}
                        onClick={() => handleOpenSources(message.response!.citations)}
                      />
                      <IconButton
                        label="Copy answer"
                        icon={copiedId === message.id ? Check : Copy}
                        onClick={() => handleCopy(message.content, message.id)}
                      />
                    </div>
                  </div>
                )}
                {message.role === 'user' && (
                  <IconButton
                    label="Retry"
                    icon={RefreshCw}
                    onClick={() => handleRetry(message)}
                  />
                )}
              </div>

              <MarkdownMessage content={message.content} />

              {/* Refusal reason */}
              {message.response?.refused && message.response.refusal_reason && (
                <div className="mt-3 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-200">
                  <ShieldAlert size={14} className="mt-0.5 shrink-0" />
                  <span>{message.response.refusal_reason}</span>
                </div>
              )}

              {/* Citation cards inline */}
              {message.response && message.response.citations.length > 0 && (
                <div className="mt-4">
                  <p className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-500">
                    Key Authorities ({message.response.citations.length})
                  </p>
                  <CitationCards citations={message.response.citations.slice(0, 3)} />
                  {message.response.citations.length > 3 && (
                    <button
                      type="button"
                      onClick={() => handleOpenSources(message.response!.citations)}
                      className="mt-2 text-xs font-medium text-docket hover:underline"
                    >
                      View all {message.response.citations.length} authorities
                    </button>
                  )}
                </div>
              )}

              {/* Feedback buttons */}
              {message.response && !message.feedback && (
                <div className="mt-4 flex items-center gap-2 border-t border-slate-100 pt-3 dark:border-slate-800">
                  <span className="text-xs text-slate-400">Was this helpful?</span>
                  <button
                    type="button"
                    onClick={() => handleFeedback(message.response!.id!, 1)}
                    className="rounded p-1 text-slate-400 transition hover:bg-slate-100 hover:text-emerald-600 dark:hover:bg-slate-800"
                    title="Thumbs up"
                  >
                    <ThumbsUp size={15} />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleFeedback(message.response!.id!, -1)}
                    className="rounded p-1 text-slate-400 transition hover:bg-slate-100 hover:text-rose-600 dark:hover:bg-slate-800"
                    title="Thumbs down"
                  >
                    <ThumbsDown size={15} />
                  </button>
                </div>
              )}

              {/* Feedback confirmation */}
              {message.feedback && (
                <div className="mt-4 flex items-center gap-2 border-t border-slate-100 pt-3 text-xs text-slate-400 dark:border-slate-800">
                  <Check size={14} className="text-emerald-500" />
                  <span>Feedback recorded</span>
                </div>
              )}
            </div>
          ))}

          {/* Loading state */}
          {chat.isPending && (
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel dark:border-slate-700 dark:bg-slate-900">
              <div className="flex items-center gap-3">
                <TypingAnimation />
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {PROGRESS_STATES[progressIndex]}
                </span>
              </div>
              {/* Progress bar */}
              <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                <div
                  className="h-full animate-pulse rounded-full bg-docket transition-all"
                  style={{
                    width: `${((progressIndex + 1) / PROGRESS_STATES.length) * 100}%`,
                  }}
                />
              </div>
              {timedOut && (
                <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
                  This is taking longer than expected. Local LLM responses may be slow on CPU.
                </p>
              )}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Scroll to bottom button */}
      {showScrollButton && (
        <div className="flex justify-center">
          <button
            type="button"
            onClick={() => scrollToBottom(true)}
            className="-mb-3 flex items-center gap-1 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-500 shadow-md transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800"
          >
            <ChevronDown size={14} />
            New messages
          </button>
        </div>
      )}

      {/* Input area */}
      <div className="border-t border-slate-200 bg-white/95 backdrop-blur dark:border-slate-700 dark:bg-slate-950/95">
        <div className="mx-auto flex max-w-4xl items-end gap-2 p-4">
          {messages.length > 0 && (
            <IconButton label="Clear chat" icon={Trash2} onClick={handleClearChat} className="shrink-0" />
          )}
          <div className="relative flex-1">
            <textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  const formEvent = { preventDefault: () => {} } as FormEvent;
                  submit(formEvent);
                }
              }}
              rows={1}
              className="min-h-12 w-full resize-none rounded-xl border-slate-300 bg-slate-50 py-3 pl-4 pr-12 text-sm shadow-sm focus:border-docket focus:ring-docket dark:border-slate-700 dark:bg-slate-900"
              placeholder="Ask about an Indian legal issue..."
              disabled={chat.isPending}
            />
            <button
              type="button"
              onClick={() => {
                const formEvent = { preventDefault: () => {} } as FormEvent;
                submit(formEvent);
              }}
              className="absolute bottom-2 right-2 inline-flex h-8 w-8 items-center justify-center rounded-lg bg-docket text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={chat.isPending || !query.trim()}
              aria-label="Send query"
              title="Send query"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
        <p className="pb-2 text-center text-[10px] text-slate-400 dark:text-slate-500">
          AI-generated legal information. Verify with a qualified lawyer.
        </p>
      </div>

      {/* Source drawer */}
      <SourceDrawer
        open={drawerOpen}
        citations={drawerCitations}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}
