"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import { useTheme } from "@/components/ThemeProvider";

const COLORS = {
  user: "#163542",
  run: "#355e49",
  park: "#355e49",
  food: "#c24e1d",
  gym: "#2f6f4e",
  grocery: "#8a5a2b",
  hangout: "#8b3a62",
  specialty: "#c24e1d",
  visit: "#1e3a4c",
  saved: "#163542",
  transit: "#1d4e89",
};

function placeKey(place) {
  return place.place_key || `${place.name}|${place.lat}|${place.lng}`;
}

function tileLayer(dark) {
  return L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 19,
    className: dark ? "la-map-tiles-dark" : "",
  });
}

export default function MapCanvas({
  center,
  places = [],
  stop = null,
  officeStop = null,
  activeTab,
  selectedKey,
  onSelect,
}) {
  const { theme } = useTheme();
  const dark = theme === "dark";
  const elRef = useRef(null);
  const mapRef = useRef(null);
  const layerRef = useRef(null);
  const tilesRef = useRef(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  useEffect(() => {
    if (!elRef.current || mapRef.current) return;
    const map = L.map(elRef.current, {
      zoomControl: true,
      attributionControl: true,
    }).setView([center.lat, center.lng], 14);

    tilesRef.current = tileLayer(dark).addTo(map);
    layerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;
    setTimeout(() => map.invalidateSize(), 150);

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    if (tilesRef.current) map.removeLayer(tilesRef.current);
    tilesRef.current = tileLayer(dark).addTo(map);
  }, [dark]);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!map || !layer || !center) return;

    layer.clearLayers();
    const bounds = [];

    L.circleMarker([center.lat, center.lng], {
      radius: 9,
      color: COLORS.user,
      weight: 2,
      fillColor: COLORS.user,
      fillOpacity: 1,
    })
      .bindPopup("You are here")
      .addTo(layer);
    bounds.push([center.lat, center.lng]);

    places.forEach((place) => {
      const key = placeKey(place);
      const selected = selectedKey === key;
      const color = COLORS[activeTab] || COLORS.park;
      const marker = L.circleMarker([place.lat, place.lng], {
        radius: selected ? 11 : 7,
        color,
        weight: selected ? 3 : 2,
        fillColor: color,
        fillOpacity: selected ? 1 : 0.85,
      }).bindPopup(
        `<strong>${place.name}</strong><br/>${place.walk_minutes} min walk${
          place.hours_label ? `<br/>${place.hours_label}` : ""
        }`,
      );
      marker.on("click", () => onSelectRef.current?.(place));
      marker.addTo(layer);
      if (selected) marker.openPopup();
      bounds.push([place.lat, place.lng]);
    });

    if (stop) {
      L.circleMarker([stop.lat, stop.lng], {
        radius: 8,
        color: COLORS.transit,
        weight: 2,
        fillColor: COLORS.transit,
        fillOpacity: 0.95,
      })
        .bindPopup(`<strong>Home stop · ${stop.name}</strong><br/>${stop.walk_minutes} min walk`)
        .addTo(layer);
      bounds.push([stop.lat, stop.lng]);
    }

    if (officeStop && (officeStop.lat !== stop?.lat || officeStop.lng !== stop?.lng)) {
      L.circleMarker([officeStop.lat, officeStop.lng], {
        radius: 8,
        color: "#c24e1d",
        weight: 2,
        fillColor: "#fff8ee",
        fillOpacity: 1,
      })
        .bindPopup(`<strong>Office stop · ${officeStop.name}</strong>`)
        .addTo(layer);
      bounds.push([officeStop.lat, officeStop.lng]);
    }

    if (bounds.length > 1 && !selectedKey) {
      map.fitBounds(bounds, { padding: [28, 28], maxZoom: 15 });
    } else {
      map.setView([center.lat, center.lng], map.getZoom() || 14);
    }
  }, [center, places, stop, officeStop, activeTab, selectedKey]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !selectedKey) return;
    const selected = places.find((place) => placeKey(place) === selectedKey);
    if (selected) {
      map.panTo([selected.lat, selected.lng]);
    }
  }, [selectedKey, places]);

  return <div ref={elRef} className="h-full w-full" />;
}
