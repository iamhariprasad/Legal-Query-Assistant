import { ArrowUpRight } from 'lucide-react';
import type { Citation } from '../../types/api';

function CourtBadge({ source }: { source: string }) {
  const lower = source.toLowerCase();
  const color = lower.includes('supreme')
    ? 'bg-violet-100 text-violet-700 dark:bg-violet-900/50 dark:text-violet-300'
    : lower.includes('high court')
      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
      : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400';

  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${color}`}>
      {source}
    </span>
  );
}

export function CitationCards({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) {
    return (
      <p className="text-sm italic text-slate-400 dark:text-slate-500">
        No verified authorities were attached.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {citations.map((citation) => (
        <a
          key={citation.document_id}
          href={citation.url}
          target="_blank"
          rel="noreferrer"
          className="group relative flex items-start gap-3 rounded-lg border border-slate-200 bg-white px-4 py-3 pl-3 transition hover:border-docket/40 hover:bg-blue-50/40 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-docket/40 dark:hover:bg-blue-950/20"
        >
          {/* Bullet marker */}
          <span
            className="mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full bg-slate-300 group-hover:bg-docket dark:bg-slate-600 dark:group-hover:bg-blue-400"
            aria-hidden="true"
          />

          <div className="min-w-0 flex-1">
            {/* Title row */}
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 group-hover:text-docket dark:group-hover:text-blue-400">
                {citation.title}
              </h3>
              <ArrowUpRight
                size={14}
                className="mt-0.5 shrink-0 text-slate-300 transition group-hover:text-docket dark:text-slate-600"
                aria-hidden="true"
              />
            </div>

            {/* Court badge */}
            <div className="mt-2">
              <CourtBadge source={citation.source} />
            </div>

            {/* Snippet */}
            {citation.snippet && (
              <p className="mt-2 line-clamp-3 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
                <span className="mr-1 text-slate-400" aria-hidden="true">→</span>
                {citation.snippet}
              </p>
            )}
          </div>
        </a>
      ))}
    </div>
  );
}
