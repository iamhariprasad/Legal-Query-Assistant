export function TypingAnimation() {
  return (
    <div className="flex items-center gap-1 text-slate-500" aria-label="Generating">
      <span className="h-2 w-2 animate-bounce rounded-full bg-current" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:120ms]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:240ms]" />
    </div>
  );
}

