const SCENES = [
  {
    src: "/auth/park.jpg",
    index: "01",
    title: "Run",
    copy: "Nearest park, walking minutes.",
  },
  {
    src: "/auth/food.jpg",
    index: "02",
    title: "Eat",
    copy: "Open kitchens nearby, in IST.",
  },
  {
    src: "/auth/commute.jpg",
    index: "03",
    title: "Leave",
    copy: "Peak windows before the crush.",
  },
];

export function AuthStage({ kicker, headline, dek }) {
  return (
    <aside className="relative flex min-h-[22rem] flex-col overflow-hidden bg-ink text-cream lg:min-h-screen">
      <div className="relative min-h-[18rem] flex-1 lg:min-h-0">
        <img
          src="/auth/park.jpg"
          alt="A quiet morning park path for a run"
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/35 to-ink/10 dark:from-black dark:via-black/50 dark:to-amber-950/25" />
        <div className="auth-grid pointer-events-none absolute inset-0 hidden opacity-60 dark:block" />
        <div className="pointer-events-none absolute -right-10 top-0 hidden h-72 w-72 rounded-full bg-ember/40 blur-3xl dark:block" />

        <div className="relative z-10 flex h-full min-h-[18rem] flex-col justify-between p-5 sm:p-8 lg:min-h-full lg:p-10">
          <p className="text-[11px] uppercase tracking-[0.28em] text-cream/70">{kicker}</p>
          <div className="max-w-xl">
            <p className="font-serif text-3xl leading-[1.08] sm:text-4xl lg:text-5xl">{headline}</p>
            <p className="mt-4 hidden max-w-md text-sm leading-relaxed text-cream/75 lg:block">{dek}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 border-t border-cream/15">
        <figure className="relative h-28 overflow-hidden sm:h-36 lg:h-44">
          <img src="/auth/food.jpg" alt="Breakfast nearby" className="h-full w-full object-cover" />
          <figcaption className="absolute inset-x-0 bottom-0 bg-ink/75 px-3 py-2 text-[10px] uppercase tracking-[0.18em]">
            Food · open now
          </figcaption>
        </figure>
        <figure className="relative h-28 overflow-hidden border-l border-cream/15 sm:h-36 lg:h-44">
          <img src="/auth/commute.jpg" alt="Local train at dusk" className="h-full w-full object-cover" />
          <figcaption className="absolute inset-x-0 bottom-0 bg-ink/75 px-3 py-2 text-[10px] uppercase tracking-[0.18em]">
            Commute · leave-by
          </figcaption>
        </figure>
      </div>

      <ul className="grid grid-cols-3 gap-3 bg-moss px-5 py-4 text-cream dark:bg-[#1a120c] dark:shadow-[inset_0_1px_0_rgba(232,137,58,0.35)] sm:px-8 lg:px-10">
        {SCENES.map((scene) => (
          <li key={scene.index}>
            <p className="text-[10px] tracking-[0.2em] text-cream/60">{scene.index}</p>
            <p className="mt-1 font-serif text-xl sm:text-2xl">{scene.title}</p>
            <p className="mt-1 hidden text-xs leading-relaxed text-cream/70 sm:block">{scene.copy}</p>
          </li>
        ))}
      </ul>
    </aside>
  );
}
