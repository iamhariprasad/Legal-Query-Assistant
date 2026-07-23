import { Database, LogOut, Server, User as UserIcon, Zap } from 'lucide-react';
import { useHealth } from '../api/hooks';
import { useAuth } from '../context/AuthContext';

export function Settings() {
  const { user, logout } = useAuth();
  const { data: health, isLoading: healthLoading } = useHealth();

  return (
    <section className="mx-auto max-w-3xl px-4 py-6">
      <h1 className="mb-6 text-xl font-semibold">Settings</h1>

      {/* User profile */}
      {user && (
        <div className="mb-4 rounded-xl border border-slate-200 bg-white p-5 shadow-panel dark:border-slate-700 dark:bg-slate-900">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">Account</h2>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-court text-white">
              <UserIcon size={22} />
            </div>
            <div>
              <p className="font-semibold text-slate-900 dark:text-slate-100">{user.full_name}</p>
              <p className="text-sm text-slate-500">{user.email}</p>
              <div className="mt-1 flex items-center gap-2">
                <span className="rounded bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  {user.role}
                </span>
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={logout}
            className="mt-4 flex items-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            <LogOut size={16} />
            Sign out
          </button>
        </div>
      )}

      {/* Backend connection status */}
      <div className="mb-4 rounded-xl border border-slate-200 bg-white p-5 shadow-panel dark:border-slate-700 dark:bg-slate-900">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">Backend Status</h2>
        {healthLoading ? (
          <p className="text-sm text-slate-500">Checking backend connection...</p>
        ) : health ? (
          <div className="space-y-2">
            <div className="flex items-center gap-3 text-sm">
              <Server size={16} className={health.status === 'ok' ? 'text-emerald-600' : 'text-rose-600'} />
              <span className="text-slate-600 dark:text-slate-300">API Status:</span>
              <span
                className={`font-medium ${health.status === 'ok' ? 'text-emerald-600' : 'text-rose-600'}`}
              >
                {health.status === 'ok' ? 'Online' : health.status}
              </span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <Database size={16} className="text-court" />
              <span className="text-slate-600 dark:text-slate-300">PostgreSQL:</span>
              <span
                className={`font-medium ${
                  health.dependencies?.postgres === 'ok' ? 'text-emerald-600' : 'text-rose-600'
                }`}
              >
                {health.dependencies?.postgres === 'ok' ? 'Connected' : health.dependencies?.postgres || 'Unknown'}
              </span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <Zap size={16} className="text-court" />
              <span className="text-slate-600 dark:text-slate-300">Redis:</span>
              <span
                className={`font-medium ${
                  health.dependencies?.redis === 'ok' ? 'text-emerald-600' : 'text-rose-600'
                }`}
              >
                {health.dependencies?.redis === 'ok' ? 'Connected' : health.dependencies?.redis || 'Unknown'}
              </span>
            </div>
            {health.dependencies?.ollama_model && (
              <div className="flex items-center gap-3 text-sm">
                <Server size={16} className="text-court" />
                <span className="text-slate-600 dark:text-slate-300">LLM Model:</span>
                <span className="font-medium text-slate-700 dark:text-slate-200">
                  {health.dependencies.ollama_model}
                </span>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-rose-600">Could not reach backend API.</p>
        )}
      </div>

      {/* About the application */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel dark:border-slate-700 dark:bg-slate-900">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">About</h2>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Legal Query Assistant v1.0.0
        </p>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          AI-powered legal research tool using retrieval-augmented generation with Indian Kanoon case law.
        </p>
      </div>
    </section>
  );
}
