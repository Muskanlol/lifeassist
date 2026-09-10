"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/components/AuthProvider";
import { SiteMark } from "@/components/SiteMark";
import ThemeToggle from "@/components/ThemeToggle";
import { api } from "@/lib/api";
import { DEMO_LOCALITIES } from "@/lib/demo";

export default function AccountPage() {
  const { user, ready, refresh, logout } = useAuth();
  const router = useRouter();
  const [home, setHome] = useState("");
  const [office, setOffice] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (ready && !user) router.replace("/login");
  }, [ready, user, router]);

  useEffect(() => {
    if (user) {
      setHome(user.home_locality || "");
      setOffice(user.office_locality || "");
    }
  }, [user]);

  async function onSubmit(event) {
    event.preventDefault();
    setPending(true);
    setError("");
    setMessage("");
    try {
      await api("/auth/me", {
        method: "PATCH",
        body: JSON.stringify({
          home_locality: home,
          office_locality: office,
        }),
      });
      await refresh();
      setMessage("Localities saved.");
    } catch (err) {
      setError(err.message);
    } finally {
      setPending(false);
    }
  }

  if (!ready || !user) {
    return <div className="grid min-h-screen place-items-center text-mute">Loading…</div>;
  }

  return (
    <div className="min-h-screen">
      <div className="h-1.5 bg-gradient-to-r from-moss via-clay to-deep" />
      <div className="mx-auto max-w-xl px-6 py-8">
        <div className="flex items-center justify-between gap-3">
          <SiteMark />
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link href="/dashboard" className="text-sm text-wine underline decoration-sand underline-offset-4">
              Back to dashboard
            </Link>
          </div>
        </div>
        <form
          onSubmit={onSubmit}
          className="mt-10 rounded-[28px] border border-sand/70 bg-surface p-7 shadow-[0_24px_60px_rgba(28,24,20,0.08)]"
        >
          <p className="text-[11px] uppercase tracking-[0.22em] text-wine">Account</p>
          <h1 className="mt-2 font-serif text-4xl">Your localities</h1>
          <p className="mt-2 text-sm text-mute">{user.email}</p>
          <p className="mt-3 text-sm text-mute">
            Leave-by times use home as origin and office as the alight-at stop. Set both for a full commute brief.
          </p>
          <label className="mt-8 block text-sm">
            Home locality
            <input
              value={home}
              onChange={(event) => setHome(event.target.value)}
              className="field-input"
            />
          </label>
          <div className="mt-3 flex flex-wrap gap-2">
            {DEMO_LOCALITIES.map((place) => (
              <button
                type="button"
                key={place.name}
                onClick={() => setHome(place.name)}
                className="rounded-full bg-fog px-3 py-1 text-xs"
              >
                {place.name}
              </button>
            ))}
          </div>
          <label className="mt-4 block text-sm">
            Office locality
            <input
              value={office}
              onChange={(event) => setOffice(event.target.value)}
              className="field-input"
            />
          </label>
          {message ? <p className="mt-4 text-sm text-moss">{message}</p> : null}
          {error ? <p className="mt-4 text-sm text-clay">{error}</p> : null}
          <button
            type="submit"
            disabled={pending}
            className="mt-6 w-full rounded-xl bg-contrast py-3.5 text-sm font-medium uppercase tracking-[0.12em] text-on-contrast disabled:opacity-60"
          >
            {pending ? "Saving…" : "Save localities"}
          </button>
        </form>
        <button
          type="button"
          onClick={() => {
            logout();
            router.push("/");
          }}
          className="mt-6 text-sm text-mute underline decoration-sand underline-offset-4"
        >
          Log out
        </button>
      </div>
    </div>
  );
}
