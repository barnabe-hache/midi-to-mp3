from fastapi import APIRouter
from pathlib import Path
from app.models.schemas import SoundfontListResponse, SoundfontInfo

router = APIRouter(prefix="/soundfonts", tags=["soundfonts"])

SOUNDFONTS_DIR = Path(__file__).resolve().parent.parent.parent / "soundfonts"

@router.get("", response_model=SoundfontListResponse)
def list_soundfonts():
    files = sorted(
        f for f in SOUNDFONTS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() == ".sf2"
    )
    soundfonts = [
        SoundfontInfo(id=f.stem, name=f.stem)  # nom = nom de fichier sans extension, tel quel
        for f in files
    ]
    return SoundfontListResponse(soundfonts=soundfonts)