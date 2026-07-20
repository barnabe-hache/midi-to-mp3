from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import soundfonts, convert, preview

app = FastAPI(title="MIDI to MP3 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(soundfonts.router)
app.include_router(soundfonts.router)
app.include_router(convert.router)
app.include_router(preview.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend opérationnel"}