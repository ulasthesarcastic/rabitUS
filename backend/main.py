"""rabitUS — Low-code Integration Platform"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import hash_password
from backend.config import settings
from backend.database import Base, engine, SessionLocal
from backend.models.user import User
from backend.models.connection import Connection  # noqa: F401 — register model
from backend.models.flow import Flow, FlowRun  # noqa: F401 — register model

from backend.api.auth_routes import router as auth_router
from backend.api.connection_routes import router as connection_router
from backend.api.flow_routes import router as flow_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed admin user
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                password_hash=hash_password("admin123"),
                full_name="Admin",
            ))
            db.commit()
    finally:
        db.close()

    yield


app = FastAPI(
    title="rabitUS",
    description="API'si olan veya olmayan iki sistemi, RQL ile tanımlayıp entegre eden platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(connection_router)
app.include_router(flow_router)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
