import { useMemo } from 'react';
import { Activity, Database, HardDrive, Server, ShieldAlert, Zap } from 'lucide-react';
import { useAdminMetrics, useGuardrails, useHealth } from '../api/hooks';
import { compactDate } from '../utils/format';
import { TypingAnimation } from '../components/chat/TypingAnimation';

function MetricCard({
  icon: Icon,
  label,
  value,
  color = 'text-court',
}: {
  icon: typeof Activity;
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel transition hover:shadow-md dark:border-slate-700 dark:bg-slate-900">
      <div className="flex items-center gap-3">
        <Icon className={color} size={22} aria-hidden="true" />
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
          <p className={`mt-1 text-2xl font-semibold ${color}`}>{value}</p>
        </div>
      </div>
    </div>
  );
}

export function AdminDashboard() {
  const metrics = useAdminMetrics();
  const guardrails = useGuardrails();
  const health = useHealth();

  // Derive computed metrics
  const computed = useMemo(() => {
    const m = metrics.data || [];
    const totalChats = m.find((x) => x.name === 'total_chats')?.value || 0;
    const totalRefusals = m.find((x) => x.name === 'total_refusals')?.value || 0;
    const avgConfidence = m.find((x) => x.name === 'avg_confidence')?.value || 0;
    const avgLatency = m.find((x) => x.name === 'avg_latency_ms')?.value || 0;
    const cacheHits = m.find((x) => x.name === 'cache_hits')?.value || 0;
    const cacheMisses = m.find((x) => x.name === 'cache_misses')?.value || 0;
    const totalSearchLogs = m.find((x) => x.name === 'total_search_logs')?.value || 0;
    const cacheHitRate = cacheHits + cacheMisses > 0 ? cacheHits / (cacheHits + cacheMisses) : 0;
    return { totalChats, totalRefusals, avgConfidence, avgLatency, cacheHits, cacheMisses, cacheHitRate, totalSearchLogs };
  }, [metrics.data]);

  // Guardrail trigger breakdown
  const guardrailBreakdown = useMemo(() => {
    const breaks: Record<string, number> = {};
    (guardrails.data || []).forEach((g) => {
      breaks[g.trigger] = (breaks[g.trigger] || 0) + 1;
    });
    return breaks;
  }, [guardrails.data]);

  const isLoading = metrics.isLoading || guardrails.isLoading || health.isLoading;
  const isError = metrics.isError || guardrails.isError || health.isError;

  if (isLoading) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-10">
        <div className="flex items-center justify-center gap-3 text-slate-500">
          <TypingAnimation />
          <span className="text-sm">Loading admin dashboard...</span>
        </div>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-10">
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-6 text-center dark:border-rose-900 dark:bg-rose-950">
          <ShieldAlert size={32} className="mx-auto mb-3 text-rose-500" />
          <p className="font-medium text-rose-800 dark:text-rose-200">Failed to load admin data</p>
          <p className="mt-2 text-sm text-rose-700 dark:text-rose-300">
            Could not fetch metrics, guardrails, or health information.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Admin Dashboard</h1>
        <span className="text-sm text-slate-500">
          Last updated: {compactDate(new Date().toISOString())}
        </span>
      </div>

      {/* System Health */}
      <div className="mb-6">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">System Health</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          {health.data?.dependencies ? (
            Object.entries(health.data.dependencies).map(([name, status]) => (
              <div
                key={name}
                className={`flex items-center gap-3 rounded-xl border p-4 shadow-panel ${
                  status === 'ok'
                    ? 'border-emerald-200 bg-emerald-50 dark:border-emerald-900 dark:bg-emerald-950'
                    : 'border-rose-200 bg-rose-50 dark:border-rose-900 dark:bg-rose-950'
                }`}
              >
                {name === 'postgres' ? (
                  <Database className={status === 'ok' ? 'text-emerald-600' : 'text-rose-600'} size={22} />
                ) : name === 'redis' ? (
                  <Zap className={status === 'ok' ? 'text-emerald-600' : 'text-rose-600'} size={22} />
                ) : (
                  <Server className="text-court" size={22} />
                )}
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{name}</p>
                  <p
                    className={`mt-0.5 text-sm font-semibold ${
                      status === 'ok' ? 'text-emerald-700 dark:text-emerald-300' : 'text-rose-700 dark:text-rose-300'
                    }`}
                  >
                    {status === 'ok' ? 'Healthy' : status}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-3 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900">
              Health data unavailable
            </div>
          )}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="mb-6">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">Operational Metrics</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard icon={Activity} label="Total Chats" value={computed.totalChats} />
          <MetricCard
            icon={ShieldAlert}
            label="Refusals"
            value={computed.totalRefusals}
            color={computed.totalRefusals > 0 ? 'text-amber-600' : 'text-court'}
          />
          <MetricCard
            icon={HardDrive}
            label="Avg Confidence"
            value={`${Math.round(computed.avgConfidence * 100)}%`}
          />
          <MetricCard icon={Zap} label="Avg Latency" value={`${Math.round(computed.avgLatency)}ms`} />
        </div>
      </div>

      {/* Redis Cache */}
      <div className="mb-6">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">Redis Cache</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard icon={Database} label="Cache Hits" value={computed.cacheHits} color="text-emerald-600" />
          <MetricCard icon={Zap} label="Cache Misses" value={computed.cacheMisses} color="text-amber-600" />
          <MetricCard
            icon={Activity}
            label="Hit Rate"
            value={computed.cacheHitRate > 0 ? `${Math.round(computed.cacheHitRate * 100)}%` : 'N/A'}
            color="text-court"
          />
          <MetricCard icon={HardDrive} label="IK Searches" value={computed.totalSearchLogs} />
        </div>
      </div>

      {/* Guardrail Breakdown */}
      {guardrails.data && guardrails.data.length > 0 && (
        <div className="mb-6">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">
            Guardrail Trigger Breakdown
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(guardrailBreakdown).map(([trigger, count]) => (
              <div
                key={trigger}
                className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel dark:border-slate-700 dark:bg-slate-900"
              >
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{trigger}</p>
                <p className="mt-1 text-2xl font-semibold text-amber-600">{count}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Guardrail Logs */}
      <div className="mb-6">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">Recent Guardrail Events</h2>
        <div className="grid gap-3">
          {guardrails.data && guardrails.data.length > 0 ? (
            guardrails.data.map((log) => (
              <div
                key={log.id}
                className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel dark:border-slate-700 dark:bg-slate-900"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <ShieldAlert size={16} className="text-amber-600" />
                    <span className="font-medium text-slate-900 dark:text-slate-100">{log.trigger}</span>
                  </div>
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-medium ${
                      log.severity === 'high'
                        ? 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-100'
                        : log.severity === 'medium'
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-100'
                          : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-100'
                    }`}
                  >
                    {log.severity}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{log.reason}</p>
                <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-400">
                  <span>Query: &ldquo;{log.query.length > 80 ? `${log.query.slice(0, 80)}...` : log.query}&rdquo;</span>
                  <span>&middot;</span>
                  <span>{compactDate(log.created_at)}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-xl border border-slate-200 bg-white p-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900">
              No guardrail events recorded yet.
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
