const accessRequestUrl =
  "https://github.com/AlejoBI/Proyecto-IS2/issues/new?title=Solicitud%20de%20acceso%20a%20la%20demo";

const DemoNotice = ({ compact = false }) => {
  if (compact) {
    return (
      <aside className="rounded-2xl border border-amber-500/25 bg-amber-500/10 p-4">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 text-lg" aria-hidden="true">
            ◌
          </span>
          <div>
            <p className="text-sm font-bold text-amber-100">Academic demo environment</p>
            <p className="mt-1 text-xs leading-5 text-amber-100/70">
              Free-tier services may sleep or reach usage limits. If the demo is unavailable,
              request an activation window from the project team.
            </p>
            <a
              href={accessRequestUrl}
              target="_blank"
              rel="noreferrer"
              className="mt-2 inline-flex text-xs font-bold text-amber-100 underline decoration-amber-300/50 underline-offset-4 transition hover:text-white"
            >
              Request test access →
            </a>
          </div>
        </div>
      </aside>
    );
  }

  return (
    <section className="relative mb-8 overflow-hidden rounded-3xl border border-amber-500/25 bg-gradient-to-br from-amber-500/15 via-slate-900 to-slate-950 p-6 shadow-xl sm:p-8">
      <div
        className="absolute -top-16 -right-12 h-40 w-40 rounded-full bg-amber-400/10 blur-2xl"
        aria-hidden="true"
      />
      <div className="relative grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center">
        <div className="max-w-3xl">
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-bold tracking-[0.18em] text-emerald-200 uppercase">
              <span className="h-2 w-2 rounded-full bg-emerald-300 shadow-[0_0_12px_rgba(110,231,183,0.8)]" />
              Demo controlada
            </span>
            <span className="text-xs font-semibold text-amber-100/60">
              Cloudflare Pages · Render · MongoDB Atlas
            </span>
          </div>
          <h2 className="mt-4 text-2xl font-black tracking-tight text-white sm:text-3xl">
            Prueba el sistema, teniendo en cuenta sus límites de infraestructura.
          </h2>
          <p className="mt-3 max-w-2xl leading-7 text-slate-300">
            Esta es una demo académica desplegada con servicios gratuitos. El backend puede tardar
            en despertar, alcanzar límites de uso o quedar temporalmente pausado. Si necesitas una
            ventana de pruebas, comunícate con el equipo del proyecto.
          </p>
        </div>
        <div className="flex flex-col gap-3 lg:min-w-52 lg:items-stretch">
          <a
            href={accessRequestUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded-xl bg-amber-300 px-5 py-3 text-center text-sm font-black text-slate-950 transition hover:bg-amber-200"
          >
            Solicitar acceso de prueba
          </a>
          <p className="text-center text-xs leading-5 text-amber-100/60 lg:max-w-52">
            La disponibilidad puede variar según la capacidad gratuita.
          </p>
        </div>
      </div>
      <div className="relative mt-6 grid gap-3 border-t border-amber-200/10 pt-5 text-xs text-slate-400 sm:grid-cols-3">
        <p>
          <span className="font-bold text-slate-200">BYOK</span> · Usa tu propia key de OpenAI o
          Gemini.
        </p>
        <p>
          <span className="font-bold text-slate-200">Privacidad</span> · La key no se almacena en
          esta aplicación.
        </p>
        <p>
          <span className="font-bold text-slate-200">Soporte</span> · Solicita activación si el
          entorno está dormido.
        </p>
      </div>
    </section>
  );
};

export default DemoNotice;
