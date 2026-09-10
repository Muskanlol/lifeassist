"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AuthStage } from "@/components/AuthStage";
import { useAuth } from "@/components/AuthProvider";
import { SiteMark } from "@/components/SiteMark";
import ThemeToggle from "@/components/ThemeToggle";
import { DEMO_LOCALITIES } from "@/lib/demo";

export default function RegisterPage() {
  const { register, user, ready } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [home, setHome] = useState("Bandra");
  const [office, setOffice] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (ready && user) router.replace("/dashboard");
  }, [ready, user, router]);

  async function onSubmit(event) {
    event.preventDefault();
    setError("");
    setPending(true);
    try {
      await register({
        email,
        password,
        home_locality: home || null,
        office_locality: office || null,
      });
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.15fr_0.85fr]">
      <AuthStage
        kicker="India · parks · food · transit"
        headline="Save your localities. Wake up to a day already planned."
        dek="Pick home and office once. Every morning you get a run, open food nearby, and a leave-by time for the station."
      />

      <div className="relative flex items-center justify-center px-5 py-10 sm:px-8">
        <form
          onSubmit={onSubmit}
          className="w-full max-w-md rounded-[28px] border border-sand/70 bg-surface p-7 shadow-[0_24px_60px_rgba(28,24,20,0.08)] sm:p-9"
        >
          <div className="flex items-center justify-between gap-3">
            <SiteMark />
            <ThemeToggle />
          </div>
          <p className="mt-8 text-[11px] uppercase tracking-[0.22em] text-wine">Create account</p>
          <h1 className="mt-2 font-serif text-4xl leading-tight">Start the day.</h1>
          <label className="mt-8 block text-sm">
            Email
            <input
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="field-input"
            />
          </label>
          <label className="mt-4 block text-sm">
            Password <span className="text-mute">(min 8 characters)</span>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="field-input"
            />
          </label>
          <label className="mt-4 block text-sm">
            Home locality
            <input
              value={home}
              onChange={(event) => setHome(event.target.value)}
              placeholder="Bandra, Jaipur, Indiranagar…"
              className="field-input"
            />
          </label>
          <div className="mt-3 flex flex-wrap gap-2">
            {DEMO_LOCALITIES.map((place) => (
              <button
                type="button"
                key={place.name}
                onClick={() => setHome(place.name)}
                className={`rounded-full px-3 py-1 text-xs ${
                  home === place.name ? "bg-contrast text-on-contrast" : "bg-fog text-ink"
                }`}
              >
                {place.name}
              </button>
            ))}
          </div>
          <label className="mt-4 block text-sm">
            Office locality <span className="text-mute">(optional)</span>
            <input
              value={office}
              onChange={(event) => setOffice(event.target.value)}
              placeholder="BKC, Andheri East, Cyber City…"
              className="field-input"
            />
          </label>
          {error ? <p className="mt-4 text-sm text-clay">{error}</p> : null}
          <button
            type="submit"
            disabled={pending}
            className="mt-6 w-full rounded-xl bg-clay py-3.5 text-sm font-medium uppercase tracking-[0.12em] text-cream disabled:opacity-60"
          >
            {pending ? "Creating account…" : "Create account"}
          </button>
          <p className="mt-6 text-sm text-mute">
            Already registered?{" "}
            <Link href="/login" className="text-wine underline decoration-sand underline-offset-4">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
