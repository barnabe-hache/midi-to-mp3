import tempfile
import shutil
import traceback
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.services.midi_render import render_midi_to_wav

router = APIRouter(prefix="/preview", tags=["preview"])

SOUNDFONTS_DIR = Path(__file__).resolve().parent.parent.parent / "soundfonts"
DEMO_MIDI_PATH = Path(__file__).resolve().parent.parent / "assets" / "demo_scale.mid"


@router.post("")
async def preview_soundfont(
    soundfont_id: str | None = Form(None),
    custom_soundfont: UploadFile | None = File(None),
):
    if not DEMO_MIDI_PATH.exists():
        raise HTTPException(500, "Demo MIDI file missing on server")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)

            if custom_soundfont is not None and custom_soundfont.filename:
                soundfont_path = tmp_dir_path / "custom.sf2"
                with soundfont_path.open("wb") as f:
                    shutil.copyfileobj(custom_soundfont.file, f)
            elif soundfont_id:
                soundfont_path = SOUNDFONTS_DIR / f"{soundfont_id}.sf2"
                if not soundfont_path.exists():
                    raise HTTPException(404, f"Soundfont '{soundfont_id}' not found")
            else:
                raise HTTPException(400, "No soundfont provided")

            output_wav_path = tmp_dir_path / "preview.wav"
            render_midi_to_wav(str(DEMO_MIDI_PATH), str(soundfont_path), str(output_wav_path))

            final_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            shutil.copy(output_wav_path, final_tmp.name)

    except HTTPException:
        raise
    except Exception as e:
        print("=== PREVIEW ERROR ===")
        traceback.print_exc()
        raise HTTPException(500, f"Error while generating preview: {e}")

    return FileResponse(final_tmp.name, media_type="audio/wav", filename="preview.wav")