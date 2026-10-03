from fastapi import FastAPI
from db.database import  create_db_and_tables
from contextlib import asynccontextmanager
from api.routes.auth import router as auth_router
from api.routes.documents import router as documents_router
from api.routes.chat import router as chat_router
from api.routes.conversations import router as conversations_router
from starlette.middleware.sessions import SessionMiddleware
from core.config import settings

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from core.limiter import limiter, rate_limit_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield



app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
)


app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(conversations_router)




@app.get("/")
def root():
    return {"message": "KnowBase API"}