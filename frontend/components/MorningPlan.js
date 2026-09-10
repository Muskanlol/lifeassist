export default function MorningPlan({ morning, leave, loading, onPick }) {
  if (loading && !morning) {
    return (
      <div className="mt-5 grid gap-3 md:grid-cols-3">
        {[0, 1, 2].map((item) => (
          <div key={item} className="h-28 animate-pulse rounded-[22px] bg-sand/60" />
        ))}
      </div>
    );
  }
  if (!morning) return null;

  const cards = [
    { id: "run", label: "Run", body: morning.run, tone: "bg-moss text-cream" },
    { id: "food", label: "Eat", body: morning.eat, tone: "bg-clay text-cream" },
    { id: "commute", label: "Leave", body: morning.commute, tone: leave?.action === "wait" ? "bg-clay text-cream" : "bg-deep text-cream" },
  ];

  const extras = [
    { id: "gym", label: "Gym", body: morning.gym },
    { id: "grocery", label: "Grocery", body: morning.grocery },
    { id: "hangout", label: "Hangout", body: morning.hangout },
    { id: "specialty", label: "Local", body: morning.specialty },
    { id: "visit", label: "Visit", body: morning.visit },
  ].filter((card) => card.body);

  return (
    <section className="mt-5">
      <div className="grid gap-3 md:grid-cols-3">
        {cards.map((card) => (
          <button
            type="button"
            key={card.label}
            onClick={() => onPick?.(card.id)}
            className={`rounded-[22px] px-5 py-4 text-left ${card.tone}`}
          >
            <p className="text-xs uppercase tracking-[0.18em] opacity-75">{card.label}</p>
            <p className="mt-2 font-serif text-xl leading-snug">{card.body}</p>
          </button>
        ))}
      </div>
      {extras.length ? (
        <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
          {extras.map((card) => (
            <button
              type="button"
              key={card.id}
              onClick={() => onPick?.(card.id)}
              className="rounded-2xl bg-fog px-4 py-3 text-left ring-1 ring-sand"
            >
              <p className="text-[11px] uppercase tracking-[0.16em] text-mute">{card.label}</p>
              <p className="mt-1 text-sm leading-snug">{card.body}</p>
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}
