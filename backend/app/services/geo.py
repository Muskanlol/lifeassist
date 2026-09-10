import math


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def walk_minutes(distance_m: float, speed_kmh: float = 4.8) -> int:
    metres_per_min = (speed_kmh * 1000) / 60
    return max(1, round(distance_m / metres_per_min))


def grid_key(category: str, lat: float, lng: float, radius: int) -> str:
    return f"v2:{category}:{round(lat, 2):.2f}:{round(lng, 2):.2f}:{int(radius)}"


def walk_cache_key(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    return f"{round(lat1, 4)}:{round(lng1, 4)}:{round(lat2, 4)}:{round(lng2, 4)}"
