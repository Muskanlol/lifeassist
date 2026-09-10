from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    home_locality: str | None = None
    office_locality: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    home_locality: str | None = None
    office_locality: str | None = None

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdateIn(BaseModel):
    home_locality: str | None = None
    office_locality: str | None = None


class LocationOut(BaseModel):
    query: str
    display_name: str
    lat: float
    lng: float
    cached: bool = False


class PlaceOut(BaseModel):
    name: str
    category: str
    lat: float
    lng: float
    distance_m: int
    walk_minutes: int
    extra: str | None = None
    place_key: str | None = None
    is_open: bool | None = None
    hours_label: str | None = None
    opening_hours: str | None = None


class PlacesResponse(BaseModel):
    origin: dict
    radius_m: int
    cached: bool
    places: list[PlaceOut]


class PeakWindowOut(BaseModel):
    line_name: str
    day_type: str
    start_time: str
    end_time: str
    note: str | None = None


class NearestStopOut(BaseModel):
    name: str
    mode: str
    lat: float
    lng: float
    distance_m: int
    walk_minutes: int
    line_guess: str
    extra: str | None = None
    cached: bool = False


class PeakInfoOut(BaseModel):
    line: str
    day_type: str
    now_ist: str
    in_peak: bool
    suggestion: str
    windows: list[PeakWindowOut]


class LeavePlanOut(BaseModel):
    action: str
    leave_home_at: str
    walk_minutes: int
    home_stop: str
    office_stop: str | None = None
    line: str
    headline: str


class CrowdSummaryOut(BaseModel):
    line: str
    mood: str | None = None
    latest: str | None = None
    counts: dict
    reports: int
    window_hours: int = 3


class CrowdIn(BaseModel):
    line: str
    level: str
    stop_name: str | None = None


class FavoriteIn(BaseModel):
    category: str
    name: str
    lat: float
    lng: float
    extra: str | None = None
    place_key: str


class FavoriteOut(BaseModel):
    id: int
    category: str
    name: str
    lat: float
    lng: float
    extra: str | None = None
    place_key: str

    model_config = {"from_attributes": True}


class MorningOut(BaseModel):
    run: str
    eat: str
    commute: str
    gym: str = ""
    grocery: str = ""
    hangout: str = ""
    specialty: str = ""
    visit: str = ""


class DayPlanOut(BaseModel):
    parks: PlacesResponse
    food: PlacesResponse
    gym: PlacesResponse
    grocery: PlacesResponse
    hangout: PlacesResponse
    specialty: PlacesResponse
    visit: PlacesResponse
    home: LocationOut
    office: LocationOut | None = None
    home_stop: NearestStopOut
    office_stop: NearestStopOut | None = None
    peak: PeakInfoOut
    leave: LeavePlanOut
    crowd: CrowdSummaryOut
    morning: MorningOut
    mode: str
