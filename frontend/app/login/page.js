"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AuthStage } from "@/components/AuthStage";
import { useAuth } from "@/components/AuthProvider";
import { SiteMark } from "@/components/SiteMark";
import ThemeToggle from "@/components/ThemeToggle";

export default function LoginPage() {
  const { login, user, ready } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
      await login(email, password);
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
        kicker="India · daily life assistant"
        headline="Parks, food, and the train — before you leave the door."
        dek="LifeAssist is a locality brief: where to run, what is open to eat, and when to leave so you miss the crush."
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
          <p className="mt-8 text-[11px] uppercase tracking-[0.22em] text-wine">Welcome back</p>
          <h1 className="mt-2 font-serif text-4xl leading-tight">Sign in</h1>
          <p className="mt-2 text-sm text-mute">Your saved localities and morning plan stay with the account.</p>
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
            Password
            <input
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="field-input"
            />
          </label>
          {error ? <p className="mt-4 text-sm text-clay">{error}</p> : null}
          <button
            type="submit"
            disabled={pending}
            className="mt-6 w-full rounded-xl bg-contrast py-3.5 text-sm font-medium tracking-[0.12em] text-on-contrast uppercase disabled:opacity-60"
          >
            {pending ? "Signing in…" : "Sign in"}
          </button>
          <p className="mt-6 text-sm text-mute">
            New here?{" "}
            <Link href="/register" className="text-wine underline decoration-sand underline-offset-4">
              Create an account
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
