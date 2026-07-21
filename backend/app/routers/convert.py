import tempfile
import shutil
import traceback
import json
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse

from app.services.midi_render import render_midi_to_wav
from app.services.effects import apply_effects
from app.services.normalize import normalize_loudness
from app.services.export import export_to_mp3
from app.models.schemas import EffectsParams
from app.limiter import limiter

router = APIRouter(prefix="/convert", tags=["convert"])

SOUNDFONTS_DIR = Path(__file__).resolve().parent.parent.parent / "soundfonts"
MAX_MIDI_SIZE_BYTES = 4 * 1024 * 1024


def _run_pipeline(midi_path, soundfont_path, params, tmp_dir_path):
    raw_wav_path = tmp_dir_path / "01_raw.wav"
    render_midi_to_wav(str(midi_path), str(soundfont_path), str(raw_wav_path))

    fx_wav_path = tmp_dir_path / "02_effects.wav"
    apply_effects(
        str(raw_wav_path),
        str(fx_wav_path),
        room_size=params.room_size,
        damping=params.damping,
        wet_level=params.wet_level,
        dry_level=params.dry_level,
        highpass_freq=params.highpass_freq,
        lowpass_freq=params.lowpass_freq,
        compression_amount=params.compression_amount,
    )

    normalized_wav_path = tmp_dir_path / "03_normalized.wav"
    normalize_loudness(str(fx_wav_path), str(normalized_wav_path), target_lufs=params.target_lufs)

    mp3_path = tmp_dir_path / "output.mp3"
    export_to_mp3(str(normalized_wav_path), str(mp3_path))

    return mp3_path


@router.post("")
@limiter.limit("100/day")
async def convert_midi_to_mp3(
    request: Request,
    midi_file: UploadFile = File(...),
    soundfont_id: str | None = Form(None),
    custom_soundfont: UploadFile | None = File(None),
    effects_params: str = Form("{}"),
):
    if not midi_file.filename.lower().endswith((".mid", ".midi")):
        raise HTTPException(400, "The file must be a .mid or .midi")

    midi_content = await midi_file.read()
    if len(midi_content) > MAX_MIDI_SIZE_BYTES:
        raise HTTPException(413, "The MIDI file exceeds the 4 MB size limit")
    await midi_file.seek(0)

    try:
        params = EffectsParams(**json.loads(effects_params))
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(400, f"Invalid effects parameters: {e}")

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
                    raise HTTPException(404, f"Soundfont '{soundfont_id}' not found")
            else:
                raise HTTPException(400, "No soundfont provided")

            try:
                mp3_path = await asyncio.wait_for(
                    asyncio.to_thread(_run_pipeline, midi_path, soundfont_path, params, tmp_dir_path),
                    timeout=90.0,
                )
            except asyncio.TimeoutError:
                raise HTTPException(504, "Processing took too long and was cancelled")

            final_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            shutil.copy(mp3_path, final_tmp.name)

    except HTTPException:
        raise
    except Exception as e:
        print("=== CONVERSION ERROR ===")
        traceback.print_exc()
        raise HTTPException(500, f"Server error during conversion: {e}")

    return FileResponse(final_tmp.name, media_type="audio/mpeg", filename="conversion.mp3")