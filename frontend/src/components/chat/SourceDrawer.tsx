import { X } from 'lucide-react';
import { CitationCards } from './CitationCards';
import type { Citation } from '../../types/api';
import { IconButton } from '../common/IconButton';

export function SourceDrawer({
  open,
  citations,
  onClose,
}: {
  open: boolean;
  citations: Citation[];
  onClose: () => void;
}) {
  return (
    <aside
      className={`fixed inset-y-0 right-0 z-40 w-full max-w-md border-l border-slate-200 bg-slate-50 p-4 shadow-xl transition-transform dark:border-slate-700 dark:bg-slate-950 ${
        open ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-semibold">Key Authorities</h2>
        <IconButton label="Close sources" icon={X} onClick={onClose} />
      </div>
      <CitationCards citations={citations} />
    </aside>
  );
}

