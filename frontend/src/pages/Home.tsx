import { ArrowRight, Database, LogIn, Scale, Search, ShieldCheck, UserPlus, Workflow } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { TypingAnimation } from '../components/chat/TypingAnimation';

export function Home() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <section className="mx-auto px-4 py-20 text-center">
        <div className="flex items-center justify-center gap-3 text-slate-500">
          <TypingAnimation />
          <span className="text-sm">Loading...</span>
        </div>
      </section>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* Hero section */}
      <div className="mb-10 text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-court/10">
          <Scale className="text-court" size={32} />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
          Legal Query Assistant
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-base text-slate-600 dark:text-slate-300">
          AI-powered Indian legal research using retrieval-augmented generation.
          Ask questions, get citation-grounded answers from Indian Kanoon case law.
        </p>
        <div className="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
          {isAuthenticated ? (
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 rounded-xl bg-docket px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
            >
              Start a query
              <ArrowRight size={18} />
            </Link>
          ) : (
            <>
              <Link
                to="/chat"
                className="inline-flex items-center gap-2 rounded-xl bg-docket px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
              >
                <LogIn size={18} />
                Sign in
              </Link>
              <Link
                to="/chat"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              >
                <UserPlus size={18} />
                Create account
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Feature cards */}
      <div className="grid gap-4 md:grid-cols-3">
        {[
          {
            title: 'Grounded Answers',
            icon: Database,
            text: 'Responses are built from retrieved Indian legal evidence. Every answer cites its sources.',
          },
          {
            title: 'Guardrail Escalation',
            icon: ShieldCheck,
            text: 'Low-confidence or unsafe requests are refused cleanly with an explanation.',
          },
          {
            title: 'LangGraph Workflow',
            icon: Workflow,
            text: 'Search, retrieve, rerank, generate, verify, and store — all in a structured pipeline.',
          },
          {
            title: 'Indian Kanoon',
            icon: Search,
            text: 'Real-time search across Indian case law via the Indian Kanoon API.',
          },
          {
            title: 'Persistent History',
            icon: Database,
            text: 'All queries and answers are stored in PostgreSQL for review and audit.',
          },
          {
            title: 'Redis Cache',
            icon: Workflow,
            text: 'Frequently accessed searches are cached in Redis for faster responses.',
          },
        ].map(({ title, icon: Icon, text }) => (
          <div
            key={title}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-panel transition hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
          >
            <Icon className="mb-3 text-court" size={22} aria-hidden="true" />
            <h2 className="font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
