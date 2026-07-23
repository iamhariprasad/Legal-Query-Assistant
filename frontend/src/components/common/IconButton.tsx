import type { ButtonHTMLAttributes, ComponentType } from 'react';
import type { LucideProps } from 'lucide-react';

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
  icon: ComponentType<LucideProps>;
}

export function IconButton({ label, icon: Icon, className = '', ...props }: IconButtonProps) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className={`inline-flex h-9 w-9 items-center justify-center rounded border border-slate-200 bg-white text-slate-700 shadow-panel transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800 ${className}`}
      {...props}
    >
      <Icon size={18} aria-hidden="true" />
    </button>
  );
}
