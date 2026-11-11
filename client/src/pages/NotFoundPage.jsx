function NotFoundPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-24 text-center">
      <p className="text-brand-100 text-sm font-bold tracking-[0.3em] uppercase">404</p>
      <h1 className="mt-4 text-5xl font-black text-white">Page not found</h1>
      <p className="mt-4 text-slate-400">The page you are looking for does not exist.</p>
      <a
        href="/"
        className="bg-brand-500 hover:bg-brand-600 mt-8 inline-flex rounded-xl px-5 py-3 font-bold text-white"
      >
        Go home
      </a>
    </main>
  );
}

export default NotFoundPage;
