"use client";

import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import { SiteMark } from "@/components/SiteMark";
import ThemeToggle from "@/components/ThemeToggle";
import { DEMO_LOCALITIES } from "@/lib/demo";

const features = [
  {
    index: "01",
    title: "Morning run",
    copy: "The nearest park with walking minutes — not a dump of every green blob on the map.",
    tone: "bg-moss text-cream",
    image: "/auth/park.jpg",
  },
  {
    index: "02",
    title: "Open now",
    copy: "Cafes and kitchens from OpenStreetMap, hours parsed against IST so you know what is actually open.",
    tone: "bg-clay text-cream",
    image: "/auth/food.jpg",
  },
  {
    index: "03",
    title: "Leave-by",
    copy: "Home stop, office stop, peak windows, and a leave-by time — not a live crowding lie.",
    tone: "bg-deep text-cream",
    image: "/auth/commute.jpg",
  },
];

const extras = [
  "Gyms, groceries, hangouts, local specialty shops, and places to visit",
  "Saved places for the spots you actually repeat",
  "Crowd reports from people on the same line",
  "Cached OSM lookups so the app stays fast and polite to free APIs",
];

export default function HomePage() {
  const { user, ready } = useAuth();

  return (
    <div className="min-h-screen">
      <div className="h-1.5 bg-gradient-to-r from-moss via-clay to-deep" />
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <SiteMark />
        <nav className="flex items-center gap-3 text-sm">
          <ThemeToggle />
          {ready && user ? (
            <Link
              href="/dashboard"
              className="rounded-full bg-contrast px-4 py-2 text-on-contrast transition hover:bg-clay hover:text-cream"
            >
              Open dashboard
            </Link>
          ) : (
            <>
              <Link href="/login" className="px-3 py-2 text-mute hover:text-ink">
                Sign in
              </Link>
              <Link
                href="/register"
                className="rounded-full bg-contrast px-4 py-2 text-on-contrast transition hover:bg-clay hover:text-cream"
              >
                Create account
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-6 pb-20">
        <section className="grid gap-10 pb-16 pt-6 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <div>
            <p className="mb-4 text-sm uppercase tracking-[0.22em] text-wine">India · daily life assistant</p>
            <h1 className="font-serif text-5xl leading-[0.95] tracking-tight sm:text-7xl">
              The day, already
              <span className="text-wine"> figured out.</span>
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-mute">
              A locality assistant for the three decisions you repeat every weekday: where to run, what is open
              nearby, and whether to leave for the station now or wait out the crush.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href={user ? "/dashboard" : "/register"}
                className="rounded-full bg-clay px-6 py-3 text-sm font-medium text-cream hover:bg-peak"
              >
                Plan today
              </Link>
              <Link href="/login" className="rounded-full border border-sand bg-surface px-6 py-3 text-sm hover:border-ink">
                I already have an account
              </Link>
            </div>
            <dl className="mt-10 grid max-w-lg grid-cols-3 gap-4 border-t border-sand pt-6">
              <div>
                <dt className="text-[11px] uppercase tracking-[0.16em] text-mute">Decisions</dt>
                <dd className="font-serif text-4xl text-wine">3</dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.16em] text-mute">Locality</dt>
                <dd className="font-serif text-4xl text-moss">1</dd>
              </div>
              <div>
                <dt className="text-[11px] uppercase tracking-[0.16em] text-mute">Clock</dt>
                <dd className="font-serif text-4xl text-deep">IST</dd>
              </div>
            </dl>
          </div>

          <aside className="grid gap-3 sm:grid-cols-2">
            <figure className="relative overflow-hidden rounded-[28px] sm:row-span-2">
              <img src="/auth/park.jpg" alt="Morning park for a run" className="h-full min-h-[280px] w-full object-cover" />
              <figcaption className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink/80 to-transparent px-4 py-4 text-cream">
                <p className="text-[10px] uppercase tracking-[0.2em] opacity-70">01</p>
                <p className="font-serif text-2xl">Run</p>
              </figcaption>
            </figure>
            <figure className="relative overflow-hidden rounded-[28px]">
              <img src="/auth/food.jpg" alt="Food nearby" className="h-40 w-full object-cover sm:h-44" />
              <figcaption className="absolute inset-x-0 bottom-0 bg-ink/70 px-4 py-3 text-cream">
                <p className="font-serif text-xl">Eat</p>
              </figcaption>
            </figure>
            <figure className="relative overflow-hidden rounded-[28px]">
              <img src="/auth/commute.jpg" alt="Local train commute" className="h-40 w-full object-cover sm:h-44" />
              <figcaption className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink/80 to-transparent px-4 py-3 text-cream">
                <p className="font-serif text-xl">Leave</p>
              </figcaption>
            </figure>
          </aside>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          {features.map((feature) => (
            <article key={feature.index} className={`overflow-hidden rounded-[24px] ${feature.tone}`}>
              <img src={feature.image} alt="" className="h-36 w-full object-cover opacity-90" />
              <div className="p-6">
                <p className="text-xs tracking-[0.2em] opacity-70">{feature.index}</p>
                <h2 className="mt-4 font-serif text-3xl">{feature.title}</h2>
                <p className="mt-3 text-sm leading-relaxed opacity-90">{feature.copy}</p>
              </div>
            </article>
          ))}
        </section>

        <section className="mt-6 grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-[28px] border border-sand bg-surface p-6 shadow-[0_20px_50px_rgba(28,24,20,0.06)]">
            <p className="text-xs uppercase tracking-[0.18em] text-wine">Demo localities</p>
            <ul className="mt-4 space-y-4">
              {DEMO_LOCALITIES.map((place) => (
                <li key={place.name} className="border-t border-sand pt-4 first:border-t-0 first:pt-0">
                  <p className="font-serif text-2xl">{place.name}</p>
                  <p className="mt-1 text-sm text-mute">{place.blurb}</p>
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-[28px] bg-deep p-8 text-cream">
            <p className="text-xs uppercase tracking-[0.18em] text-cream/60">Built like a product</p>
            <h2 className="mt-3 font-serif text-3xl">Not a map dump. A daily brief.</h2>
            <ul className="mt-6 space-y-3 text-sm text-cream/80">
              {extras.map((item) => (
                <li key={item} className="flex gap-3">
                  <span className="mt-1 h-1.5 w-1.5 rounded-full bg-ember" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
    </div>
  );
}
