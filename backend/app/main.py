import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import auth, comments, notifications, posts, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Local Finder API", lifespan=lifespan)

# Allowed CORS Origins
origins = [
    "https://nearby-watch.netlify.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

# Include FRONTEND_URL if set in environment
if hasattr(settings, "FRONTEND_URL") and settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*--nearby-watch\.netlify\.app",  # Matches Netlify previews
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads/posts", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/api/")
async def health():
    return {"status": "ok", "service": "local-finder-api"}


app.include_router(auth.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(ws.router)  # /ws/notifications — no /api prefix