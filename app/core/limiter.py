from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Limit by IP 
limiter = Limiter(key_func=get_remote_address)




async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    limit = getattr(exc, "limit", None)


    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests",
        },
    )