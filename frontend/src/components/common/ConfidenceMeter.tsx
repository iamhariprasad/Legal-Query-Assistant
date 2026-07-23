import { percent } from '../../utils/format';

export function ConfidenceMeter({ value }: { value: number }) {
  const color = value >= 0.75 ? 'bg-court' : value >= 0.62 ? 'bg-brief' : 'bg-rose-600';
  return (
    <div className="min-w-40">
      <div className="mb-1 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>Confidence</span>
        <span>{percent(value)}</span>
      </div>
      <div className="h-2 rounded bg-slate-200 dark:bg-slate-700">
        <div className={`h-2 rounded ${color}`} style={{ width: percent(value) }} />
      </div>
    </div>
  );
}

