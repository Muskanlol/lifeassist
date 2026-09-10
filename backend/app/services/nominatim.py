import httpx

from app.config import settings
from app.services.rate_limit import nominatim_limiter

HEADERS = {
    "User-Agent": settings.nominatim_user_agent,
    "Accept-Language": "en-IN,en",
}


async def geocode_india(query: str) -> dict | None:
    await nominatim_limiter.wait()
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "in",
        "addressdetails": 1,
    }
    async with httpx.AsyncClient(timeout=20.0, headers=HEADERS) as client:
        res = await client.get(settings.nominatim_url, params=params)
        res.raise_for_status()
        data = res.json()
    if not data:
        return None
    hit = data[0]
    return {
        "display_name": hit.get("display_name") or query,
        "lat": float(hit["lat"]),
        "lng": float(hit["lon"]),
    }


async def suggest_india(query: str, limit: int = 5) -> list[dict]:
    await nominatim_limiter.wait()
    params = {
        "q": f"{query}, India",
        "format": "json",
        "limit": limit,
        "countrycodes": "in",
        "addressdetails": 1,
    }
    async with httpx.AsyncClient(timeout=20.0, headers=HEADERS) as client:
        res = await client.get(settings.nominatim_url, params=params)
        res.raise_for_status()
        data = res.json()
    results = []
    seen = set()
    for hit in data:
        display = hit.get("display_name") or query
        key = display.lower()
        if key in seen:
            continue
        seen.add(key)
        results.append(
            {
                "query": display.split(",")[0].strip(),
                "display_name": display,
                "lat": float(hit["lat"]),
                "lng": float(hit["lon"]),
            }
        )
    return results
