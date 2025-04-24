from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database import database
from src.config import settings, limiter
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware
from src.modules.classroom.routes import router as classroom_router
from src.modules.group.routes import router as group_router
from src.modules.pensum.routes import router as pensum_router
from src.modules.subject.routes import router as subject_router
from src.modules.academic_schedule.routes import router as academic_schedule_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)



@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def initialize():
    return {"message": "Hello from FastAPI"}


origins = settings.ALLOWED_HOSTS.split(",")

app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.include_router(classroom_router, prefix="/classroom")
app.include_router(group_router, prefix="/group")
app.include_router(pensum_router, prefix="/pensum")
app.include_router(subject_router, prefix="/subject")
app.include_router(academic_schedule_router, prefix="/academic_schedule")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

