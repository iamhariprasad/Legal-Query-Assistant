export function About() {
  return (
    <section className="mx-auto max-w-3xl px-4 py-6">
      <h1 className="mb-4 text-xl font-semibold">About</h1>
      <div className="rounded border border-slate-200 bg-white p-4 text-sm leading-6 shadow-panel dark:border-slate-700 dark:bg-slate-900">
        <p>
          This assistant provides legal information from retrieved Indian legal sources. It is designed to refuse unsupported
          answers and direct users to qualified lawyers when confidence or citations are insufficient.
        </p>
      </div>
    </section>
  );
}

