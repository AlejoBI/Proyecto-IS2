const CustomSpinner = () => (
  <div className="flex min-h-40 items-center justify-center" role="status" aria-label="Loading">
    <span className="border-t-brand-500 h-10 w-10 animate-spin rounded-full border-4 border-slate-700" />
  </div>
);

export default CustomSpinner;
