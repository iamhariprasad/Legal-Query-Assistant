import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <section className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-semibold">Page not found</h1>
      <Link to="/chat" className="mt-4 inline-block rounded bg-docket px-4 py-2 text-sm font-medium text-white">
        Open chat
      </Link>
    </section>
  );
}

