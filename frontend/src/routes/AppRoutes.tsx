import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { useAuth } from '../context/AuthContext';
import { About } from '../pages/About';
import { AdminDashboard } from '../pages/AdminDashboard';
import { Chat } from '../pages/Chat';
import { EvaluationDashboard } from '../pages/EvaluationDashboard';
import { History } from '../pages/History';
import { Home } from '../pages/Home';
import { NotFound } from '../pages/NotFound';
import { Search } from '../pages/Search';
import { Settings } from '../pages/Settings';

function AdminGuard({ children }: { children: React.ReactNode }) {
  const { isAdmin, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <div className="flex items-center gap-2 text-slate-500">
          <div className="h-2 w-2 animate-bounce rounded-full bg-current" />
          <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:120ms]" />
          <div className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:240ms]" />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  if (!isAdmin) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-10 text-center">
        <h1 className="text-2xl font-semibold text-slate-800 dark:text-slate-100">Access Denied</h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          You need administrator privileges to access this page.
        </p>
      </section>
    );
  }

  return <>{children}</>;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/history" element={<History />} />
        <Route path="/search" element={<Search />} />
        <Route path="/evaluation" element={<EvaluationDashboard />} />
        <Route
          path="/admin"
          element={
            <AdminGuard>
              <AdminDashboard />
            </AdminGuard>
          }
        />
        <Route path="/settings" element={<Settings />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
