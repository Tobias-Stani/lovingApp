from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.models import User, Trip
from app.routers import auth, profile, trips, admin, places, couple

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LovingApp API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(trips.router)
app.include_router(admin.router)
app.include_router(places.router)
app.include_router(couple.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
