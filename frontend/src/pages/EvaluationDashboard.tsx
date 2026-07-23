import { BarChart3, Download } from 'lucide-react';
import { useEvaluation } from '../api/hooks';
import { percent } from '../utils/format';
import { TypingAnimation } from '../components/chat/TypingAnimation';

export function EvaluationDashboard() {
  const { data, isLoading, error, isError } = useEvaluation();
  const summary = data?.summary;
  const results = data?.results || [];

  const metricCards = summary
    ? [
        { label: 'Citation Accuracy', value: summary.citation_accuracy, color: 'text-court' },
        { label: 'Precision', value: summary.precision, color: 'text-court' },
        { label: 'Recall', value: summary.recall, color: 'text-court' },
        { label: 'Faithfulness', value: summary.faithfulness, color: 'text-court' },
        { label: 'Hallucination Rate', value: summary.hallucination_rate, color: 'text-rose-600' },
        { label: 'Context Recall', value: summary.context_recall, color: 'text-court' },
      ]
    : [];

  // Loading state
  if (isLoading) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-10">
        <div className="flex items-center justify-center gap-3 text-slate-500">
          <TypingAnimation />
          <span className="text-sm">Loading evaluation results...</span>
        </div>
      </section>
    );
  }

  // Error state
  if (isError) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-10">
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-6 text-center dark:border-rose-900 dark:bg-rose-950">
          <p className="font-medium text-rose-800 dark:text-rose-200">Failed to load evaluation data</p>
          <p className="mt-2 text-sm text-rose-700 dark:text-rose-300">
            {error?.message || 'Could not fetch evaluation results.'}
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Evaluation Dashboard</h1>
          {summary && (
            <p className="mt-1 text-sm text-slate-500">
              {summary.total} benchmark queries evaluated
            </p>
          )}
        </div>
        {results.length > 0 && (
          <button
            type="button"
            className="flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <Download size={16} />
            Export
          </button>
        )}
      </div>

      {/* Aggregate metrics */}
      {summary ? (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {metricCards.map(({ label, value, color }) => (
              <div
                key={label}
                className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel transition hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
              >
                <p className="text-sm font-medium text-slate-500">{label}</p>
                <p className={`mt-2 text-3xl font-bold ${color}`}>{percent(value)}</p>
                {/* Mini progress bar */}
                <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                  <div
                    className={`h-full rounded-full ${value >= 0.8 ? 'bg-court' : value >= 0.6 ? 'bg-amber-500' : 'bg-rose-500'}`}
                    style={{ width: percent(value) }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Average latency */}
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel dark:border-slate-700 dark:bg-slate-900">
              <p className="text-sm font-medium text-slate-500">Average Latency</p>
              <p className="mt-2 text-3xl font-bold text-court">{Math.round(summary.avg_latency_ms)}ms</p>
            </div>
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-white p-10 text-center dark:border-slate-700 dark:bg-slate-900">
          <BarChart3 size={40} className="mb-3 text-slate-300 dark:text-slate-600" />
          <h2 className="font-medium text-slate-600 dark:text-slate-300">No evaluation data</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Run the evaluation pipeline to see benchmark results.
          </p>
        </div>
      )}

      {/* Per-query results table */}
      {results.length > 0 && (
        <div className="mt-6">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">
            Per-Query Results ({results.length})
          </h2>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-panel dark:border-slate-700 dark:bg-slate-900">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left dark:bg-slate-800">
                <tr>
                  <th className="p-3 font-medium text-slate-600 dark:text-slate-300">Query</th>
                  <th className="p-3 font-medium text-slate-600 dark:text-slate-300">Issue</th>
                  <th className="p-3 font-medium text-slate-600 dark:text-slate-300">Citation</th>
                  <th className="p-3 font-medium text-slate-600 dark:text-slate-300">Faithfulness</th>
                  <th className="p-3 font-medium text-slate-600 dark:text-slate-300">Precision</th>
                  <th className="p-3 font-medium text-slate-600 dark:text-slate-300">Recall</th>
                  <th className="p-3 font-medium text-slate-600 dark:text-slate-300">Latency</th>
                </tr>
              </thead>
              <tbody>
                {results.map((row) => (
                  <tr
                    key={row.id}
                    className="border-t border-slate-200 transition hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800/50"
                  >
                    <td className="max-w-60 truncate p-3 text-slate-800 dark:text-slate-200" title={row.query}>
                      {row.query}
                    </td>
                    <td className="p-3 text-slate-600 dark:text-slate-300">{row.expected_issue}</td>
                    <td className="p-3">
                      <span
                        className={`font-medium ${
                          row.citation_accuracy >= 0.8
                            ? 'text-court'
                            : row.citation_accuracy >= 0.6
                              ? 'text-amber-600'
                              : 'text-rose-600'
                        }`}
                      >
                        {percent(row.citation_accuracy)}
                      </span>
                    </td>
                    <td className="p-3 text-slate-600 dark:text-slate-300">{percent(row.faithfulness)}</td>
                    <td className="p-3 text-slate-600 dark:text-slate-300">{percent(row.precision)}</td>
                    <td className="p-3 text-slate-600 dark:text-slate-300">{percent(row.recall)}</td>
                    <td className="p-3 text-slate-600 dark:text-slate-300">{row.latency_ms}ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
