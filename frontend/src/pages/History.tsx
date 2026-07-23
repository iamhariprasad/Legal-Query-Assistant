import { Clock, History as HistoryIcon } from 'lucide-react';
import { useHistory } from '../api/hooks';
import { CitationCards } from '../components/chat/CitationCards';
import { compactDate, percent } from '../utils/format';
import { TypingAnimation } from '../components/chat/TypingAnimation';

export function History() {
  const { data, isLoading, error, isError } = useHistory();

  // Loading state
  if (isLoading) {
    return (
      <section className="mx-auto max-w-5xl px-4 py-10">
        <div className="flex items-center justify-center gap-3 text-slate-500">
          <TypingAnimation />
          <span className="text-sm">Loading chat history...</span>
        </div>
      </section>
    );
  }

  // Error state
  if (isError) {
    return (
      <section className="mx-auto max-w-5xl px-4 py-10">
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-6 text-center dark:border-rose-900 dark:bg-rose-950">
          <p className="font-medium text-rose-800 dark:text-rose-200">Failed to load history</p>
          <p className="mt-2 text-sm text-rose-700 dark:text-rose-300">
            {error?.message || 'Could not fetch chat history. The backend may be unavailable.'}
          </p>
        </div>
      </section>
    );
  }

  // Empty state
  if (!data || data.length === 0) {
    return (
      <section className="mx-auto max-w-5xl px-4 py-10">
        <h1 className="mb-6 text-xl font-semibold">History</h1>
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-white p-10 text-center dark:border-slate-700 dark:bg-slate-900">
          <HistoryIcon size={40} className="mb-3 text-slate-300 dark:text-slate-600" />
          <h2 className="font-medium text-slate-600 dark:text-slate-300">No chat history yet</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Your past conversations will appear here after you ask questions in the chat.
          </p>
        </div>
      </section>
    );
  }

  // Data state
  return (
    <section className="mx-auto max-w-5xl px-4 py-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold">History</h1>
        <span className="text-sm text-slate-500">
          {data.length} {data.length === 1 ? 'conversation' : 'conversations'}
        </span>
      </div>
      <div className="flex flex-col gap-4">
        {data.map((item) => (
          <article
            key={item.id}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel transition hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
          >
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <Clock size={13} />
                {compactDate(item.created_at)}
              </span>
              <div className="flex items-center gap-3">
                <span className={item.refused ? 'text-amber-600' : ''}>
                  {percent(item.confidence)} confidence
                </span>
                {item.refused && (
                  <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-100">
                    Refused
                  </span>
                )}
                <span className="text-slate-400">{item.latency_ms}ms</span>
              </div>
            </div>
            <h2 className="mt-2 font-semibold text-slate-900 dark:text-slate-100">{item.query}</h2>
            <p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
              {item.answer}
            </p>
            {item.refused && item.refusal_reason && (
              <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">{item.refusal_reason}</p>
            )}
            {item.citations && item.citations.length > 0 && (
              <div className="mt-3">
                <CitationCards citations={item.citations} />
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
