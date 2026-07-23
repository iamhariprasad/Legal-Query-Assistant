import { BarChart3, BookOpenText, History, Home, Info, Search, Settings, ShieldCheck, LogIn } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function Sidebar() {
  const { isAuthenticated, isAdmin } = useAuth();

  const links = [
    { to: '/', label: 'Home', icon: Home, authRequired: false },
    { to: '/chat', label: 'Chat', icon: BookOpenText, authRequired: true },
    { to: '/history', label: 'History', icon: History, authRequired: true },
    { to: '/search', label: 'Search', icon: Search, authRequired: true },
    { to: '/evaluation', label: 'Evaluation', icon: BarChart3, authRequired: true },
    { to: '/admin', label: 'Admin', icon: ShieldCheck, authRequired: true, adminOnly: true },
    { to: '/settings', label: 'Settings', icon: Settings, authRequired: true },
    { to: '/about', label: 'About', icon: Info, authRequired: false },
  ];

  const visibleLinks = links.filter((link) => {
    if (link.adminOnly) return isAdmin;
    if (link.authRequired) return isAuthenticated;
    return true;
  });

  return (
    <nav className="hidden w-56 shrink-0 border-r border-slate-200 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-950 md:block">
      <div className="flex h-full flex-col gap-1">
        {visibleLinks.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-2 rounded px-3 py-2 text-sm transition ${
                isActive
                  ? 'bg-court text-white'
                  : 'text-slate-700 hover:bg-slate-200 dark:text-slate-200 dark:hover:bg-slate-800'
              }`
            }
          >
            <Icon size={17} aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
        {!isAuthenticated && (
          <NavLink
            to="/chat"
            className="mt-auto flex items-center gap-2 rounded px-3 py-2 text-sm text-slate-500 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            <LogIn size={17} aria-hidden="true" />
            <span>Sign in</span>
          </NavLink>
        )}
      </div>
    </nav>
  );
}
