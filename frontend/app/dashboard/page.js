"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/components/AuthProvider";
import LocalitySearch from "@/components/LocalitySearch";
import MorningPlan from "@/components/MorningPlan";
import { SiteMark } from "@/components/SiteMark";
import ThemeToggle from "@/components/ThemeToggle";
import { api, formatDistance } from "@/lib/api";
import { DEMO_LOCALITIES } from "@/lib/demo";

const MapCanvas = dynamic(() => import("@/components/MapCanvas"), { ssr: false });

const TABS = [
  { id: "run", label: "Run" },
  { id: "food", label: "Food" },
  { id: "gym", label: "Gym" },
  { id: "grocery", label: "Grocery" },
  { id: "hangout", label: "Hangout" },
  { id: "specialty", label: "Local" },
  { id: "visit", label: "Visit" },
  { id: "commute", label: "Commute" },
  { id: "saved", label: "Saved" },
];

const LIST_FROM = {
  run: "parks",
  food: "food",
  gym: "gym",
  grocery: "grocery",
  hangout: "hangout",
  specialty: "specialty",
  visit: "visit",
};

const OPEN_TABS = new Set(["food", "gym", "grocery", "hangout", "specialty"]);

const MODES = [
  { id: "train", label: "Train" },
  { id: "metro", label: "Metro" },
  { id: "bus", label: "Bus" },
];

function keyOf(place) {
  return place?.place_key || `${place?.name}|${place?.lat}|${place?.lng}`;
}

export default function DashboardPage() {
  const { user, ready, logout, refresh } = useAuth();
  const router = useRouter();
  const [query, setQuery] = useState("Bandra");
  const [location, setLocation] = useState(null);
  const [tab, setTab] = useState("run");
  const [mode, setMode] = useState("train");
  const [plan, setPlan] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [selected, setSelected] = useState(null);
  const [openNow, setOpenNow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (ready && !user) router.replace("/login");
  }, [ready, user, router]);

  useEffect(() => {
    if (!user) return;
    const start = user.home_locality || "Bandra";
    setQuery(start);
    loadLocality(start);
    api("/favorites").then(setFavorites).catch(() => setFavorites([]));
  }, [user]);

  async function loadLocality(name, coords = null) {
    setError("");
    setSelected(null);
    if (!plan) setLoading(true);
    else setRefreshing(true);
    try {
      const resolved =
        coords && coords.lat
          ? {
              query: coords.query || name,
              display_name: coords.display_name || name,
              lat: coords.lat,
              lng: coords.lng,
              cached: true,
            }
          : await api(`/location/resolve?query=${encodeURIComponent(name)}`);
      setLocation(resolved);
      setQuery(resolved.query || name);
      const data = await api(
        `/day/plan?lat=${resolved.lat}&lng=${resolved.lng}&mode=${mode}`,
      );
      setPlan(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  async function changeMode(nextMode) {
    setMode(nextMode);
    if (!location) return;
    setRefreshing(true);
    try {
      const data = await api(
        `/day/plan?lat=${location.lat}&lng=${location.lng}&mode=${nextMode}`,
      );
      setPlan(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setRefreshing(false);
    }
  }

  async function useDeviceLocation() {
    if (!navigator.geolocation) {
      setError("Location is not available on this browser");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        await loadLocality("Current location", {
          query: "Current location",
          display_name: "Current location",
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        });
      },
      () => setError("Could not read device location"),
    );
  }

  async function saveLocality(field) {
    if (!query) return;
    try {
      await api("/auth/me", {
        method: "PATCH",
        body: JSON.stringify({ [field]: query }),
      });
      await refresh();
      setStatus(field === "home_locality" ? "Home updated." : "Office updated.");
    } catch (err) {
      setError(err.message);
    }
  }

  async function toggleFavorite(place, category) {
    const key = keyOf(place);
    const existing = favorites.find((item) => item.place_key === key);
    try {
      if (existing) {
        await api(`/favorites/${existing.id}`, { method: "DELETE" });
        setFavorites((current) => current.filter((item) => item.id !== existing.id));
      } else {
        const row = await api("/favorites", {
          method: "POST",
          body: JSON.stringify({
            category,
            name: place.name,
            lat: place.lat,
            lng: place.lng,
            extra: place.extra || place.hours_label,
            place_key: key,
          }),
        });
        setFavorites((current) => [row, ...current]);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function reportCrowd(level) {
    if (!plan?.peak?.line) return;
    try {
      const crowd = await api("/commute/crowd", {
        method: "POST",
        body: JSON.stringify({
          line: plan.peak.line,
          level,
          stop_name: plan.home_stop?.name,
        }),
      });
      setPlan((current) => ({ ...current, crowd }));
      setStatus("Crowd report saved for the next 3 hours.");
    } catch (err) {
      setError(err.message);
    }
  }

  const sourceKey = LIST_FROM[tab];
  const rawList = tab === "saved" ? favorites : sourceKey ? plan?.[sourceKey]?.places || [] : [];
  const list = OPEN_TABS.has(tab) && openNow ? rawList.filter((item) => item.is_open) : rawList;
  const mapPlaces = tab === "commute" ? [] : list;
  const cachedHint = sourceKey ? plan?.[sourceKey]?.cached : plan?.home_stop?.cached;

  const selectedKey = selected ? keyOf(selected) : null;

  const greeting = useMemo(() => {
    const hour = Number((plan?.peak?.now_ist || "09:00").split(":")[0]);
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  }, [plan]);

  if (!ready || !user) {
    return <div className="grid min-h-screen place-items-center text-mute">Loading…</div>;
  }

  return (
    <div className="min-h-screen">
      <div className="h-1.5 bg-linear-to-r from-moss via-clay to-deep" />
      <header className="border-b border-sand/80 bg-surface/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <Link href="/">
            <SiteMark />
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <ThemeToggle />
            <span className="hidden text-mute sm:inline">{user.email}</span>
            <Link href="/account" className="text-wine underline decoration-sand underline-offset-4">
              Account
            </Link>
            <button
              type="button"
              onClick={() => {
                logout();
                router.push("/");
              }}
              className="rounded-full border border-sand bg-fog px-3 py-1.5"
            >
              Log out
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-5 py-6">
        <p className="text-sm uppercase tracking-[0.18em] text-wine">
          {greeting}
          {plan?.peak?.now_ist ? ` · ${plan.peak.now_ist} IST` : ""}
          {refreshing ? " · updating" : ""}
        </p>
        <p className="font-serif text-3xl sm:text-4xl">Your day at a glance</p>
        <p className="mt-1 text-sm text-mute">
          Parks, open food, and a leave-by time from {user.home_locality || "home"}
          {user.office_locality ? ` to ${user.office_locality}` : ""}.
        </p>

        <div className="mt-6">
          <LocalitySearch
            value={query}
            onChange={setQuery}
            onPick={(item) => loadLocality(item.query, item)}
            onSubmit={() => loadLocality(query)}
            onUseLocation={useDeviceLocation}
          />
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {DEMO_LOCALITIES.map((place) => (
            <button
              type="button"
              key={place.name}
              onClick={() => loadLocality(place.query, place)}
              className={`rounded-full px-3 py-1.5 text-sm ${
                query.toLowerCase() === place.name.toLowerCase()
                  ? "bg-clay text-cream"
                  : "bg-sand/70 text-ink"
              }`}
            >
              {place.name}
            </button>
          ))}
          <button type="button" onClick={() => saveLocality("home_locality")} className="rounded-full border border-sand px-3 py-1.5 text-sm">
            Set as home
          </button>
          <button type="button" onClick={() => saveLocality("office_locality")} className="rounded-full border border-sand px-3 py-1.5 text-sm">
            Set as office
          </button>
        </div>

        {error ? <p className="mt-4 text-sm text-clay">{error}</p> : null}
        {status ? <p className="mt-2 text-sm text-moss">{status}</p> : null}

        <MorningPlan
          morning={plan?.morning}
          leave={plan?.leave}
          loading={loading}
          onPick={(id) => setTab(id)}
        />

        {plan?.leave ? (
          <div
            className={`mt-4 rounded-[22px] px-5 py-4 ${
              plan.leave.action === "wait" ? "bg-clay text-cream" : "bg-moss text-cream"
            }`}
          >
            <p className="text-xs uppercase tracking-[0.18em] opacity-80">
              Leave-by · {plan.leave.line} · {plan.leave.action.replace("_", " ")}
            </p>
            <p className="mt-1 font-serif text-2xl leading-snug">{plan.leave.headline}</p>
          </div>
        ) : null}

        <div className="mt-6 grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
          <section className="h-105 overflow-hidden rounded-[28px] border border-sand bg-surface lg:h-160">
            {location ? (
              <MapCanvas
                center={location}
                places={mapPlaces}
                stop={tab === "commute" ? plan?.home_stop : null}
                officeStop={tab === "commute" ? plan?.office_stop : null}
                activeTab={tab}
                selectedKey={selectedKey}
                onSelect={(place) => {
                  setSelected(place);
                  if (tab === "saved") return;
                  if (place.category && ["restaurant", "cafe", "fast_food", "food_court"].includes(place.category)) {
                    setTab("food");
                  }
                }}
              />
            ) : (
              <div className="grid h-105 place-items-center text-mute">Pick a locality to load the map</div>
            )}
          </section>

          <section className="rounded-[28px] border border-sand bg-surface p-4 sm:p-5">
            <div className="flex items-center justify-between gap-3">
              <div className="flex flex-wrap gap-1 rounded-2xl bg-fog p-1">
                {TABS.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setTab(item.id)}
                    className={`rounded-full px-3 py-1.5 text-sm ${
                      tab === item.id ? "bg-contrast text-on-contrast" : "text-mute"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
              {cachedHint ? <span className="text-xs text-mute">Cached</span> : null}
            </div>

            {OPEN_TABS.has(tab) ? (
              <label className="mt-3 flex items-center gap-2 text-sm">
                <input type="checkbox" checked={openNow} onChange={(event) => setOpenNow(event.target.checked)} />
                Open now
              </label>
            ) : null}

            {loading && !plan ? (
              <div className="mt-4 space-y-3">
                {[0, 1, 2, 3].map((item) => (
                  <div key={item} className="h-16 animate-pulse rounded-2xl bg-fog" />
                ))}
              </div>
            ) : null}

            {tab === "commute" ? (
              <div className="mt-4">
                <div className="flex gap-2">
                  {MODES.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => changeMode(item.id)}
                      className={`rounded-full px-3 py-1.5 text-sm ${
                        mode === item.id ? "bg-deep text-cream" : "bg-fog text-ink"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
                {plan?.home_stop ? (
                  <div className="mt-4 rounded-2xl bg-fog px-4 py-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-mute">Home stop</p>
                    <p className="mt-1 font-serif text-3xl">{plan.home_stop.name}</p>
                    <p className="mt-2 text-sm text-mute">
                      {formatDistance(plan.home_stop.distance_m)} · {plan.home_stop.walk_minutes} min walk
                    </p>
                    <p className="mt-2 text-sm">{plan.home_stop.line_guess}</p>
                  </div>
                ) : null}
                {plan?.office_stop ? (
                  <div className="mt-3 rounded-2xl bg-fog px-4 py-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-mute">Office stop</p>
                    <p className="mt-1 font-serif text-2xl">{plan.office_stop.name}</p>
                    <p className="mt-2 text-sm text-mute">
                      {formatDistance(plan.office_stop.distance_m)} · {plan.office_stop.walk_minutes} min walk
                    </p>
                  </div>
                ) : (
                  <p className="mt-3 text-sm text-mute">Add an office locality in Account to get an alight-at stop.</p>
                )}
                <div className="mt-4 rounded-2xl bg-fog px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-mute">Crowd right now</p>
                  <p className="mt-1 text-sm">
                    {plan?.crowd?.reports
                      ? `${plan.crowd.reports} report${plan.crowd.reports === 1 ? "" : "s"} in 3h · mostly ${plan.crowd.mood}`
                      : "No live reports yet. Be the first on this line."}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {[
                      ["empty", "Empty"],
                      ["ok", "OK"],
                      ["packed", "Packed"],
                    ].map(([level, label]) => (
                      <button
                        key={level}
                        type="button"
                        onClick={() => reportCrowd(level)}
                        className="rounded-full bg-surface px-3 py-1.5 text-xs"
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
                {plan?.peak?.windows?.length ? (
                  <ul className="mt-4 space-y-2">
                    {plan.peak.windows.map((window) => (
                      <li key={`${window.start_time}-${window.end_time}`} className="rounded-2xl bg-fog px-4 py-3">
                        <p className="text-sm font-medium">
                          {window.start_time} – {window.end_time}
                        </p>
                        <p className="mt-1 text-xs leading-relaxed text-mute">{window.note}</p>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            ) : (
              <ul className="mt-4 max-h-130 space-y-3 overflow-auto pr-1">
                {list.length === 0 && !loading ? (
                  <li className="rounded-2xl bg-fog px-4 py-6 text-sm text-mute">
                    {tab === "saved"
                      ? "Save parks and cafes with the heart to build your usual day."
                      : openNow
                        ? "Nothing marked open right now. Turn off the filter to see all OSM places."
                        : "OpenStreetMap has little coverage here. Try Bandra, Borivali or Mira Road."}
                  </li>
                ) : (
                  list.map((place) => {
                    const key = keyOf(place);
                    const saved = favorites.some((item) => item.place_key === key);
                    const active = selectedKey === key;
                    return (
                      <li key={key}>
                        <button
                          type="button"
                          onClick={() => setSelected(place)}
                          className={`w-full rounded-2xl px-4 py-3 text-left ${
                            active ? "bg-contrast text-on-contrast" : "bg-fog"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <p className="font-medium">{place.name}</p>
                              <p className={`mt-1 text-xs capitalize ${active ? "text-on-contrast/70" : "text-mute"}`}>
                                {(place.hours_label || place.extra || place.category || "").replaceAll("_", " ")}
                              </p>
                            </div>
                            <div className="text-right text-sm">
                              {place.distance_m != null ? <p>{formatDistance(place.distance_m)}</p> : null}
                              {place.walk_minutes != null ? (
                                <p className={active ? "text-on-contrast/70" : "text-mute"}>{place.walk_minutes} min walk</p>
                              ) : null}
                            </div>
                          </div>
                        </button>
                        {tab !== "commute" ? (
                          <button
                            type="button"
                            onClick={() => toggleFavorite(place, tab === "saved" ? place.category : tab)}
                            className="mt-1 text-xs text-mute"
                          >
                            {saved ? "Saved · tap to remove" : "Save to my day"}
                          </button>
                        ) : null}
                      </li>
                    );
                  })
                )}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
