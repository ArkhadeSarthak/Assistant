from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.utils.logger import app_logger
from app.database.session import engine, Base
from app.api.routes import chat, voice, upload, tool, memory, agent, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info(f"Starting {settings.PROJECT_NAME} (v{settings.VERSION})...")
    # Initialize database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app_logger.info("Database schema initialized successfully.")
    yield
    app_logger.info("Shutting down AURA AI Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-Ready Universal AI Agent Backend powered by FastAPI, LangChain, and LangGraph.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    app_logger.info(f"Incoming request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        app_logger.info(f"Response status: {response.status_code} for {request.url.path}")
        return response
    except Exception as e:
        app_logger.error(f"Unhandled exception during {request.method} {request.url.path}: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal Server Error", "details": str(e)}
        )

# Register Routers
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(upload.router)
app.include_router(tool.router)
app.include_router(memory.router)
app.include_router(agent.router)
app.include_router(health.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
