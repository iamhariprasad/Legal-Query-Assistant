import { FormEvent, useState } from 'react';
import { Database, ExternalLink, Search as SearchIcon } from 'lucide-react';
import { useLegalSearch } from '../api/hooks';

export function Search() {
  const [query, setQuery] = useState('');
  const search = useLegalSearch();

  function submit(event: FormEvent) {
    event.preventDefault();
    if (query.trim() && !search.isPending) {
      search.mutate(query.trim());
    }
  }

  return (
    <section className="mx-auto max-w-5xl px-4 py-6">
      <h1 className="mb-4 text-xl font-semibold">Search Indian Kanoon</h1>

      <form onSubmit={submit} className="flex gap-2">
        <div className="relative flex-1">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="w-full rounded-xl border-slate-300 py-3 pl-4 pr-10 text-sm focus:border-docket focus:ring-docket dark:border-slate-700 dark:bg-slate-900"
            placeholder="Search Indian Kanoon for case law, statutes, and legal documents..."
            disabled={search.isPending}
          />
        </div>
        <button
          className="inline-flex items-center gap-2 rounded-xl bg-court px-5 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-court/90 disabled:cursor-not-allowed disabled:bg-slate-400"
          type="submit"
          disabled={search.isPending || !query.trim()}
        >
          {search.isPending ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
          ) : (
            <SearchIcon size={17} />
          )}
          {search.isPending ? 'Searching...' : 'Search'}
        </button>
      </form>

      {/* Cache hit indicator */}
      {search.data && (
        <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
          {search.data.cache_hit ? (
            <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
              <Database size={13} />
              Cached result
            </span>
          ) : (
            <span className="flex items-center gap-1">
              <Database size={13} />
              Live search
            </span>
          )}
          <span className="text-slate-400">&middot;</span>
          <span>{search.data.found} results found</span>
          <span className="text-slate-400">&middot;</span>
          <span>{search.data.latency_ms}ms</span>
        </div>
      )}

      {/* Loading state */}
      {search.isPending && (
        <div className="mt-5 grid gap-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="animate-pulse rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900"
            >
              <div className="mb-2 h-5 w-3/4 rounded bg-slate-200 dark:bg-slate-700" />
              <div className="mb-3 h-3 w-1/2 rounded bg-slate-200 dark:bg-slate-700" />
              <div className="h-4 w-full rounded bg-slate-200 dark:bg-slate-700" />
              <div className="mt-2 h-4 w-2/3 rounded bg-slate-200 dark:bg-slate-700" />
            </div>
          ))}
        </div>
      )}

      {/* Error state */}
      {search.isError && (
        <div className="mt-5 rounded-xl border border-rose-200 bg-rose-50 p-5 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
          Search failed. Please check your Indian Kanoon API token and try again.
        </div>
      )}

      {/* Empty state */}
      {search.data && search.data.results.length === 0 && !search.isPending && (
        <div className="mt-5 flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-white p-10 text-center dark:border-slate-700 dark:bg-slate-900">
          <SearchIcon size={40} className="mb-3 text-slate-300 dark:text-slate-600" />
          <h2 className="font-medium text-slate-600 dark:text-slate-300">No results found</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Try a different search term or check your Indian Kanoon API configuration.
          </p>
        </div>
      )}

      {/* Results */}
      <div className="mt-5 grid gap-3">
        {search.data?.results.map((result) => (
          <a
            key={result.document_id}
            href={result.url}
            target="_blank"
            rel="noreferrer"
            className="group rounded-xl border border-slate-200 bg-white p-5 shadow-panel transition hover:border-docket hover:shadow-md dark:border-slate-700 dark:bg-slate-900 dark:hover:border-docket/50"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="font-semibold text-slate-900 group-hover:text-docket dark:text-slate-100">
                  {result.title}
                </h2>
                <p className="mt-0.5 text-xs text-slate-500">{result.source}</p>
              </div>
              <ExternalLink size={16} className="shrink-0 text-docket opacity-0 transition group-hover:opacity-100" />
            </div>
            <p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
              {result.headline}
            </p>
            {result.citations && result.citations.length > 0 && (
              <p className="mt-2 text-xs text-slate-400">
                Cited in {result.citations.length} document{result.citations.length !== 1 ? 's' : ''}
              </p>
            )}
          </a>
        ))}
      </div>
    </section>
  );
}
