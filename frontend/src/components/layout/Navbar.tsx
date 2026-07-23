import { useState } from 'react';
import { LogOut, Moon, Scale, Sun, User as UserIcon, Menu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { IconButton } from '../common/IconButton';

export function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 px-4 backdrop-blur dark:border-slate-700 dark:bg-slate-950/95">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <Menu size={20} />
          </button>
          <Scale className="text-court" size={22} aria-hidden="true" />
          <span className="text-sm font-semibold">Legal Query Assistant</span>
        </div>
        <div className="flex items-center gap-3">
          {isAuthenticated && user && (
            <div className="hidden items-center gap-2 text-sm text-slate-600 dark:text-slate-300 md:flex">
              <UserIcon size={16} className="text-court" aria-hidden="true" />
              <span className="max-w-40 truncate">{user.full_name}</span>
              {user.role === 'admin' && (
                <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-100">
                  Admin
                </span>
              )}
            </div>
          )}
          <IconButton label="Toggle theme" icon={theme === 'dark' ? Sun : Moon} onClick={toggleTheme} />
          {isAuthenticated && (
            <IconButton label="Sign out" icon={LogOut} onClick={logout} />
          )}
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && isAuthenticated && user && (
        <div className="border-t border-slate-200 px-4 py-3 text-sm text-slate-600 dark:border-slate-700 dark:text-slate-300 md:hidden">
          <div className="flex items-center gap-2">
            <UserIcon size={16} className="text-court" />
            <span className="font-medium">{user.full_name}</span>
            {user.role === 'admin' && (
              <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800">
                Admin
              </span>
            )}
          </div>
          <p className="mt-1 text-xs text-slate-500">{user.email}</p>
        </div>
      )}
    </header>
  );
}
