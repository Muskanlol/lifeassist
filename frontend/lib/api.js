export const TOKEN_KEY = "lifeassist_token";

function detailMessage(detail) {
  if (!detail) return "Request failed";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || item.detail || "Invalid input").join(", ");
  return "Request failed";
}

export async function api(path, options = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`/api${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (res.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
    const publicPath =
      path.startsWith("/auth/") ||
      window.location.pathname === "/" ||
      window.location.pathname.startsWith("/login") ||
      window.location.pathname.startsWith("/register");
    if (!publicPath) {
      window.location.href = "/login";
    }
  }

  if (!res.ok) {
    throw new Error(detailMessage(data.detail));
  }
  return data;
}

export function formatDistance(metres) {
  if (metres < 1000) return `${metres} m`;
  return `${(metres / 1000).toFixed(1)} km`;
}
