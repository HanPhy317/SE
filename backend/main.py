"""校园跑腿Web平台 - FastAPI JSON API Backend

Architecture:
- API Layer: JSON REST endpoints (routes/)
- Business Logic Layer: Managers (managers/)
- Data Access Layer: SQLAlchemy ORM (models/)
- Frontend: Vue 3 SPA (separate Vite project)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import APP_TITLE, APP_VERSION, CORS_ORIGINS, HOST, PORT
from database import engine, init_db
from routes.auth import auth_router
from routes.orders import order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=APP_TITLE, version=APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(order_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
