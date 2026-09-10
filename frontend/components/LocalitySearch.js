"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { DEMO_LOCALITIES } from "@/lib/demo";

export default function LocalitySearch({ value, onChange, onPick, onSubmit, onUseLocation }) {
  const [open, setOpen] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const timer = useRef(null);

  useEffect(() => {
    if (!value || value.length < 2) {
      setSuggestions(DEMO_LOCALITIES.map((item) => ({ query: item.name, display_name: item.blurb, ...item })));
      return;
    }
    clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      try {
        const data = await api(`/location/suggest?query=${encodeURIComponent(value)}`);
        setSuggestions(data.suggestions || []);
      } catch {
        setSuggestions([]);
      }
    }, 350);
    return () => clearTimeout(timer.current);
  }, [value]);

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        setOpen(false);
        onSubmit();
      }}
      className="relative"
    >
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <input
            value={value}
            onChange={(event) => {
              onChange(event.target.value);
              setOpen(true);
            }}
            onFocus={() => setOpen(true)}
            placeholder="Andheri, Koramangala, Connaught Place…"
            className="w-full rounded-full border border-sand bg-surface px-5 py-3 outline-none ring-wine focus:ring-2"
          />
          {open && suggestions.length > 0 ? (
            <ul className="absolute z-20 mt-2 w-full overflow-hidden rounded-2xl border border-sand bg-surface shadow-lg">
              {suggestions.map((item) => (
                <li key={`${item.display_name}-${item.lat}`}>
                  <button
                    type="button"
                    className="w-full px-4 py-3 text-left hover:bg-fog"
                    onClick={() => {
                      setOpen(false);
                      onPick(item);
                    }}
                  >
                    <p className="text-sm font-medium">{item.query}</p>
                    <p className="text-xs text-mute">{item.display_name}</p>
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
        <button type="submit" className="rounded-full bg-contrast px-5 py-3 text-on-contrast">
          Plan my day
        </button>
        <button type="button" onClick={onUseLocation} className="rounded-full border border-sand px-5 py-3">
          Use my location
        </button>
      </div>
    </form>
  );
}
