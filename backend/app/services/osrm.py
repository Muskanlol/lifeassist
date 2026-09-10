import httpx

from app.config import settings
from app.services.geo import haversine_m, walk_minutes
from app.services.rate_limit import osrm_limiter


async def walking_route(lat1: float, lng1: float, lat2: float, lng2: float) -> dict | None:
    await osrm_limiter.wait()
    url = (
        f"{settings.osrm_url}/route/v1/walking/"
        f"{lng1},{lat1};{lng2},{lat2}?overview=false&alternatives=false"
    )
    try:
        async with httpx.AsyncClient(timeout=12.0, headers={"User-Agent": settings.nominatim_user_agent}) as client:
            res = await client.get(url)
            if res.status_code != 200:
                return None
            data = res.json()
        routes = data.get("routes") or []
        if not routes:
            return None
        distance = float(routes[0]["distance"])
        duration = float(routes[0]["duration"])
        return {
            "distance_m": distance,
            "duration_s": duration,
            "walk_minutes": max(1, round(duration / 60)),
            "source": "osrm",
        }
    except Exception:
        return None


def estimate_walk(lat1: float, lng1: float, lat2: float, lng2: float) -> dict:
    distance = haversine_m(lat1, lng1, lat2, lng2)
    return {
        "distance_m": distance,
        "duration_s": walk_minutes(distance) * 60,
        "walk_minutes": walk_minutes(distance),
        "source": "estimate",
    }
