import tempfile
import shutil
import traceback
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.services.midi_render import render_midi_to_wav

router = APIRouter(prefix="/render", tags=["render"])

SOUNDFONTS_DIR = Path(__file__).resolve().parent.parent.parent / "soundfonts"

@router.post("")
async def render_midi(
    midi_file: UploadFile = File(...),
    soundfont_id: str | None = Form(None),
    custom_soundfont: UploadFile | None = File(None),
):
    if not midi_file.filename.lower().endswith((".mid", ".midi")):
        raise HTTPException(400, "Le fichier doit être un .mid ou .midi")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)

            midi_path = tmp_dir_path / "input.mid"
            with midi_path.open("wb") as f:
                shutil.copyfileobj(midi_file.file, f)

            if custom_soundfont is not None and custom_soundfont.filename:
                soundfont_path = tmp_dir_path / "custom.sf2"
                with soundfont_path.open("wb") as f:
                    shutil.copyfileobj(custom_soundfont.file, f)
            elif soundfont_id:
                soundfont_path = SOUNDFONTS_DIR / f"{soundfont_id}.sf2"
                if not soundfont_path.exists():
                    raise HTTPException(404, f"Soundfont '{soundfont_id}' introuvable")
            else:
                raise HTTPException(400, "Aucun soundfont fourni (ni id, ni fichier custom)")

            output_wav_path = tmp_dir_path / "output.wav"
            render_midi_to_wav(str(midi_path), str(soundfont_path), str(output_wav_path))

            final_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            shutil.copy(output_wav_path, final_tmp.name)

    except HTTPException:
        raise
    except Exception as e:
        print("=== ERREUR PENDANT LE RENDU ===")
        traceback.print_exc()
        raise HTTPException(500, f"Erreur serveur pendant le rendu: {e}")

    return FileResponse(
        final_tmp.name,
        media_type="audio/wav",
        filename="preview.wav",
    )