import { FormEvent, useState } from 'react';
import { AlertCircle, CheckCircle, LogIn, UserPlus } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface ApiError {
  code?: string;
  message?: string;
}

function extractErrorMessage(error: unknown): string {
  if (!error) return '';
  const err = error as { response?: { data?: ApiError }; message?: string };
  if (err.response?.data?.message) return err.response.data.message;
  if (err.response?.data?.code === 'email_exists') return 'This email is already registered. Try logging in instead.';
  if (err.message?.includes('401')) return 'Invalid email or password. Please try again.';
  if (err.message) return err.message;
  return 'Something went wrong. Please check your connection and try again.';
}

export function AuthPanel() {
  const { login, register, error, clearError, isAuthenticated, isLoading } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setSuccessMessage('');
    clearError();

    try {
      if (mode === 'register') {
        await register(email, fullName, password);
        setSuccessMessage('Account created successfully!');
      } else {
        await login(email, password);
      }
    } catch {
      // Error is captured by useAuth
    } finally {
      setSubmitting(false);
    }
  }

  function switchMode(newMode: 'login' | 'register') {
    setMode(newMode);
    clearError();
    setSuccessMessage('');
  }

  if (isAuthenticated) {
    return (
      <div className="mx-auto mt-8 max-w-md rounded border border-emerald-200 bg-emerald-50 p-5 shadow-panel dark:border-emerald-900 dark:bg-emerald-950">
        <div className="flex items-center gap-3">
          <CheckCircle className="text-emerald-600" size={24} />
          <div>
            <h2 className="font-semibold text-emerald-800 dark:text-emerald-200">You are signed in</h2>
            <p className="mt-1 text-sm text-emerald-700 dark:text-emerald-300">
              Start asking legal questions in the chat.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const submitLabel = mode === 'login' ? 'Sign in' : 'Create account';
  const isBusy = submitting || isLoading;

  return (
    <div className="mx-auto mt-8 max-w-md rounded border border-slate-200 bg-white p-6 shadow-panel dark:border-slate-700 dark:bg-slate-900">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold">{mode === 'login' ? 'Welcome back' : 'Create an account'}</h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
            {mode === 'login'
              ? 'Sign in to query the legal assistant.'
              : 'Register to start using the legal assistant.'}
          </p>
        </div>
        {mode === 'login' ? <LogIn className="text-court shrink-0" size={22} /> : <UserPlus className="text-court shrink-0" size={22} />}
      </div>

      <div className="mb-5 grid grid-cols-2 rounded-lg border border-slate-200 p-0.5 dark:border-slate-700">
        <button
          type="button"
          onClick={() => switchMode('login')}
          className={`rounded-md px-3 py-2 text-sm font-medium transition ${
            mode === 'login'
              ? 'bg-court text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200'
          }`}
        >
          Sign in
        </button>
        <button
          type="button"
          onClick={() => switchMode('register')}
          className={`rounded-md px-3 py-2 text-sm font-medium transition ${
            mode === 'register'
              ? 'bg-court text-white shadow-sm'
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200'
          }`}
        >
          Register
        </button>
      </div>

      <form onSubmit={submit} className="space-y-4">
        <div>
          <label htmlFor="auth-email" className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
            Email address
          </label>
          <input
            id="auth-email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border-slate-300 text-sm focus:border-docket focus:ring-docket dark:border-slate-700 dark:bg-slate-950"
            type="email"
            placeholder="you@example.com"
            required
            autoComplete="email"
          />
        </div>

        {mode === 'register' && (
          <div>
            <label htmlFor="auth-name" className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              Full name
            </label>
            <input
              id="auth-name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-lg border-slate-300 text-sm focus:border-docket focus:ring-docket dark:border-slate-700 dark:bg-slate-950"
              placeholder="John Doe"
              required
              autoComplete="name"
            />
          </div>
        )}

        <div>
          <label htmlFor="auth-password" className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
            Password
          </label>
          <input
            id="auth-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border-slate-300 text-sm focus:border-docket focus:ring-docket dark:border-slate-700 dark:bg-slate-950"
            type="password"
            minLength={mode === 'register' ? 10 : 1}
            placeholder={mode === 'register' ? 'At least 10 characters' : 'Enter your password'}
            required
            autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
          />
        </div>

        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2.5 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            <span>{extractErrorMessage(error)}</span>
          </div>
        )}

        {successMessage && (
          <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">
            <CheckCircle size={16} className="shrink-0" />
            <span>{successMessage}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={isBusy}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-docket px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-docket focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-400 dark:focus:ring-offset-slate-900"
        >
          {isBusy ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              {mode === 'login' ? 'Signing in...' : 'Creating account...'}
            </>
          ) : (
            submitLabel
          )}
        </button>
      </form>

      {mode === 'login' ? (
        <p className="mt-4 text-center text-xs text-slate-500 dark:text-slate-400">
          Don&apos;t have an account?{' '}
          <button
            type="button"
            onClick={() => switchMode('register')}
            className="font-medium text-docket hover:underline"
          >
            Register here
          </button>
        </p>
      ) : (
        <p className="mt-4 text-center text-xs text-slate-500 dark:text-slate-400">
          Already have an account?{' '}
          <button
            type="button"
            onClick={() => switchMode('login')}
            className="font-medium text-docket hover:underline"
          >
            Sign in
          </button>
        </p>
      )}
    </div>
  );
}
