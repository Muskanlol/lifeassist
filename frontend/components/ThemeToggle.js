"use client";

import { useTheme } from "@/components/ThemeProvider";

export default function ThemeToggle() {
  const { theme, toggle } = useTheme();
  const dark = theme === "dark";

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      className="inline-flex items-center gap-2 rounded-full border border-sand bg-surface px-3 py-1.5 text-sm text-ink"
    >
      <span
        className={`grid h-4 w-4 place-items-center rounded-full ${
          dark ? "bg-ember" : "bg-wine"
        }`}
      />
      {dark ? "Dark" : "Light"}
    </button>
  );
}
