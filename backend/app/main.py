import os
from dotenv import load_dotenv

load_dotenv()
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.limiter import limiter
from app.routers import soundfonts, convert, preview

app = FastAPI(title="MIDI to MP3 API")
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Daily conversion limit reached (10 per day). Please try again tomorrow."},
    )


app.include_router(soundfonts.router)
app.include_router(convert.router)
app.include_router(preview.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend opérationnel"}