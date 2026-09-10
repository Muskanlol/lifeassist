from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routers import auth, commute, day, favorites, food, location, parks, places
from app.seed import seed_peak_hours


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_peak_hours(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="LifeAssist API",
    description="Hyperlocal daily assistant for parks, food, and commute timing across India.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(location.router)
app.include_router(parks.router)
app.include_router(food.router)
app.include_router(places.router)
app.include_router(commute.router)
app.include_router(day.router)
app.include_router(favorites.router)


@app.get("/health")
def health():
    return {"ok": True, "service": "lifeassist"}
