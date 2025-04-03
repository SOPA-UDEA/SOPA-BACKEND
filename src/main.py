from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import database
import config
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(
    title=config.PROJECT_NAME,
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {"status": "ok"}
origins = config.ALLOWED_HOSTS.split(",")

app.state.limiter = config.limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
