import httpx

from app.config import settings
from app.services.rate_limit import overpass_limiter

HEADERS = {"User-Agent": settings.nominatim_user_agent}


PARK_QUERY = """
[out:json][timeout:25];
(
  nwr["leisure"="park"](around:{radius},{lat},{lng});
  nwr["leisure"="recreation_ground"](around:{radius},{lat},{lng});
  nwr["leisure"="garden"](around:{radius},{lat},{lng});
  nwr["leisure"="nature_reserve"](around:{radius},{lat},{lng});
);
out center tags;
"""

FOOD_QUERY = """
[out:json][timeout:25];
(
  nwr["amenity"="restaurant"](around:{radius},{lat},{lng});
  nwr["amenity"="cafe"](around:{radius},{lat},{lng});
  nwr["amenity"="fast_food"](around:{radius},{lat},{lng});
  nwr["amenity"="food_court"](around:{radius},{lat},{lng});
);
out center tags;
"""

TRANSIT_TRAIN_QUERY = """
[out:json][timeout:25];
(
  nwr["railway"="station"](around:{radius},{lat},{lng});
  nwr["railway"="halt"](around:{radius},{lat},{lng});
);
out center tags;
"""

TRANSIT_METRO_QUERY = """
[out:json][timeout:25];
(
  nwr["station"="subway"](around:{radius},{lat},{lng});
  nwr["railway"="subway_entrance"](around:{radius},{lat},{lng});
  nwr["railway"="station"]["station"="subway"](around:{radius},{lat},{lng});
  nwr["railway"="station"]["name"~"Metro",i](around:{radius},{lat},{lng});
);
out center tags;
"""

TRANSIT_BUS_QUERY = """
[out:json][timeout:25];
(
  nwr["highway"="bus_stop"](around:{radius},{lat},{lng});
  nwr["amenity"="bus_station"](around:{radius},{lat},{lng});
);
out center tags;
"""

EXPLORE_QUERY = """
[out:json][timeout:25];
(
  nwr["leisure"="fitness_centre"](around:{radius},{lat},{lng});
  nwr["leisure"="sports_centre"](around:{radius},{lat},{lng});
  nwr["amenity"="gym"](around:{radius},{lat},{lng});
  nwr["leisure"="fitness_station"](around:{radius},{lat},{lng});
  nwr["leisure"="swimming_pool"](around:{radius},{lat},{lng});
  nwr["shop"="supermarket"](around:{radius},{lat},{lng});
  nwr["shop"="convenience"](around:{radius},{lat},{lng});
  nwr["shop"="greengrocer"](around:{radius},{lat},{lng});
  nwr["shop"="grocery"](around:{radius},{lat},{lng});
  nwr["shop"="butcher"](around:{radius},{lat},{lng});
  nwr["amenity"="cinema"](around:{radius},{lat},{lng});
  nwr["amenity"="theatre"](around:{radius},{lat},{lng});
  nwr["amenity"="bar"](around:{radius},{lat},{lng});
  nwr["amenity"="pub"](around:{radius},{lat},{lng});
  nwr["amenity"="nightclub"](around:{radius},{lat},{lng});
  nwr["amenity"="arts_centre"](around:{radius},{lat},{lng});
  nwr["leisure"="bowling_alley"](around:{radius},{lat},{lng});
  nwr["amenity"="marketplace"](around:{radius},{lat},{lng});
  nwr["shop"="bakery"](around:{radius},{lat},{lng});
  nwr["shop"="confectionery"](around:{radius},{lat},{lng});
  nwr["shop"="tea"](around:{radius},{lat},{lng});
  nwr["shop"="spices"](around:{radius},{lat},{lng});
  nwr["shop"="gift"](around:{radius},{lat},{lng});
  nwr["tourism"="attraction"](around:{radius},{lat},{lng});
  nwr["tourism"="museum"](around:{radius},{lat},{lng});
  nwr["tourism"="viewpoint"](around:{radius},{lat},{lng});
  nwr["tourism"="gallery"](around:{radius},{lat},{lng});
  nwr["tourism"="zoo"](around:{radius},{lat},{lng});
  nwr["historic"="monument"](around:{radius},{lat},{lng});
  nwr["historic"="memorial"](around:{radius},{lat},{lng});
  nwr["historic"="fort"](around:{radius},{lat},{lng});
);
out center tags;
"""

GYM_QUERY = """
[out:json][timeout:25];
(
  nwr["leisure"="fitness_centre"](around:{radius},{lat},{lng});
  nwr["leisure"="sports_centre"](around:{radius},{lat},{lng});
  nwr["amenity"="gym"](around:{radius},{lat},{lng});
  nwr["leisure"="fitness_station"](around:{radius},{lat},{lng});
  nwr["leisure"="swimming_pool"](around:{radius},{lat},{lng});
);
out center tags;
"""

GROCERY_QUERY = """
[out:json][timeout:25];
(
  nwr["shop"="supermarket"](around:{radius},{lat},{lng});
  nwr["shop"="convenience"](around:{radius},{lat},{lng});
  nwr["shop"="greengrocer"](around:{radius},{lat},{lng});
  nwr["shop"="grocery"](around:{radius},{lat},{lng});
  nwr["shop"="butcher"](around:{radius},{lat},{lng});
);
out center tags;
"""

HANGOUT_QUERY = """
[out:json][timeout:25];
(
  nwr["amenity"="cinema"](around:{radius},{lat},{lng});
  nwr["amenity"="theatre"](around:{radius},{lat},{lng});
  nwr["amenity"="bar"](around:{radius},{lat},{lng});
  nwr["amenity"="pub"](around:{radius},{lat},{lng});
  nwr["amenity"="nightclub"](around:{radius},{lat},{lng});
  nwr["amenity"="arts_centre"](around:{radius},{lat},{lng});
  nwr["leisure"="bowling_alley"](around:{radius},{lat},{lng});
);
out center tags;
"""

SPECIALTY_QUERY = """
[out:json][timeout:25];
(
  nwr["amenity"="marketplace"](around:{radius},{lat},{lng});
  nwr["shop"="bakery"](around:{radius},{lat},{lng});
  nwr["shop"="confectionery"](around:{radius},{lat},{lng});
  nwr["shop"="tea"](around:{radius},{lat},{lng});
  nwr["shop"="spices"](around:{radius},{lat},{lng});
  nwr["shop"="gift"](around:{radius},{lat},{lng});
);
out center tags;
"""

VISIT_QUERY = """
[out:json][timeout:25];
(
  nwr["tourism"="attraction"](around:{radius},{lat},{lng});
  nwr["tourism"="museum"](around:{radius},{lat},{lng});
  nwr["tourism"="viewpoint"](around:{radius},{lat},{lng});
  nwr["tourism"="gallery"](around:{radius},{lat},{lng});
  nwr["tourism"="zoo"](around:{radius},{lat},{lng});
  nwr["historic"="monument"](around:{radius},{lat},{lng});
  nwr["historic"="memorial"](around:{radius},{lat},{lng});
  nwr["historic"="fort"](around:{radius},{lat},{lng});
);
out center tags;
"""

QUERIES = {
    "park": PARK_QUERY,
    "restaurant": FOOD_QUERY,
    "transit_stop": TRANSIT_TRAIN_QUERY,
    "transit_train": TRANSIT_TRAIN_QUERY,
    "transit_metro": TRANSIT_METRO_QUERY,
    "transit_bus": TRANSIT_BUS_QUERY,
    "explore": EXPLORE_QUERY,
    "gym": GYM_QUERY,
    "grocery": GROCERY_QUERY,
    "hangout": HANGOUT_QUERY,
    "specialty": SPECIALTY_QUERY,
    "visit": VISIT_QUERY,
}

EXPLORE_CATEGORIES = ["gym", "grocery", "hangout", "specialty", "visit"]


def _coords(element: dict) -> tuple[float, float] | None:
    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])
    center = element.get("center")
    if center and "lat" in center and "lon" in center:
        return float(center["lat"]), float(center["lon"])
    return None


def parse_elements(category: str, elements: list[dict]) -> list[dict]:
    places = []
    seen = set()
    for el in elements:
        tags = el.get("tags") or {}
        coords = _coords(el)
        if not coords:
            continue
        lat, lng = coords
        name = tags.get("name") or tags.get("name:en") or tags.get("ref")
        if not name:
            continue
        key = (round(lat, 5), round(lng, 5), name.lower())
        if key in seen:
            continue
        seen.add(key)
        extra = _extra(category, tags)
        kind = extra.get("kind") or category
        if category == "explore":
            kind = classify_place(tags)
            if not kind:
                continue
            extra = _extra(kind, tags)
        places.append(
            {
                "name": name,
                "category": kind,
                "lat": lat,
                "lng": lng,
                "extra": extra.get("label"),
                "raw_tags": tags,
            }
        )
    return places


def classify_place(tags: dict) -> str | None:
    leisure = tags.get("leisure") or ""
    amenity = tags.get("amenity") or ""
    shop = tags.get("shop") or ""
    tourism = tags.get("tourism") or ""
    historic = tags.get("historic") or ""
    if leisure in {"fitness_centre", "sports_centre", "fitness_station", "swimming_pool"} or amenity == "gym":
        return "gym"
    if shop in {"supermarket", "convenience", "greengrocer", "grocery", "butcher", "department_store"}:
        return "grocery"
    if tourism in {"attraction", "museum", "viewpoint", "gallery", "zoo", "theme_park"} or historic in {
        "monument",
        "memorial",
        "fort",
        "ruins",
        "castle",
    }:
        return "visit"
    if amenity in {"cinema", "theatre", "bar", "pub", "nightclub", "arts_centre", "ice_cream"} or leisure in {
        "bowling_alley",
        "amusement_arcade",
    }:
        return "hangout"
    if amenity == "marketplace" or shop in {"bakery", "confectionery", "tea", "spices", "gift", "pastry", "chocolate"}:
        return "specialty"
    return None


def _extra(category: str, tags: dict) -> dict:
    if category == "park":
        kind = tags.get("leisure") or "park"
        return {"kind": "park", "label": kind.replace("_", " ")}
    if category == "restaurant":
        amenity = tags.get("amenity") or "restaurant"
        cuisine = (tags.get("cuisine") or "").replace(";", ", ").replace("_", " ")
        return {"kind": amenity, "label": cuisine or amenity.replace("_", " ")}
    if category == "gym":
        label = (tags.get("leisure") or tags.get("amenity") or "gym").replace("_", " ")
        return {"kind": "gym", "label": label}
    if category == "grocery":
        return {"kind": "grocery", "label": (tags.get("shop") or "grocery").replace("_", " ")}
    if category == "hangout":
        label = (tags.get("amenity") or tags.get("leisure") or "hangout").replace("_", " ")
        return {"kind": "hangout", "label": label}
    if category == "specialty":
        label = (tags.get("shop") or tags.get("amenity") or "local").replace("_", " ")
        return {"kind": "specialty", "label": label}
    if category == "visit":
        label = (tags.get("tourism") or tags.get("historic") or "attraction").replace("_", " ")
        return {"kind": "visit", "label": label}
    network = tags.get("network") or tags.get("operator") or tags.get("line") or ""
    kind = "transit"
    if tags.get("highway") == "bus_stop" or tags.get("amenity") == "bus_station":
        kind = "bus"
    elif tags.get("station") == "subway" or "metro" in (tags.get("network") or "").lower():
        kind = "metro"
    elif tags.get("railway") in {"station", "halt"}:
        kind = "train"
    return {"kind": kind, "label": network or kind}


async def query_overpass(category: str, lat: float, lng: float, radius: int) -> list[dict]:
    template = QUERIES[category]
    q = template.format(radius=int(radius), lat=lat, lng=lng)
    await overpass_limiter.wait()
    last_error = None
    for url in (settings.overpass_url, settings.overpass_fallback_url):
        try:
            async with httpx.AsyncClient(timeout=12.0, headers=HEADERS) as client:
                res = await client.post(url, data={"data": q})
                res.raise_for_status()
                payload = res.json()
            return parse_elements(category, payload.get("elements") or [])
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Overpass unavailable: {last_error}")
