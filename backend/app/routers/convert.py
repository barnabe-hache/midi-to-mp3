import tempfile
import shutil
import traceback
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.services.midi_render import render_midi_to_wav
from app.services.effects import apply_effects
from app.services.normalize import normalize_loudness
from app.services.export import export_to_mp3
from app.models.schemas import EffectsParams

router = APIRouter(prefix="/convert", tags=["convert"])

SOUNDFONTS_DIR = Path(__file__).resolve().parent.parent.parent / "soundfonts"


@router.post("")
async def convert_midi_to_mp3(
    midi_file: UploadFile = File(...),
    soundfont_id: str | None = Form(None),
    custom_soundfont: UploadFile | None = File(None),
    effects_params: str = Form("{}"),  # JSON stringifié envoyé par le front
):
    if not midi_file.filename.lower().endswith((".mid", ".midi")):
        raise HTTPException(400, "Le fichier doit être un .mid ou .midi")

    try:
        params = EffectsParams(**json.loads(effects_params))
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(400, f"Paramètres d'effets invalides: {e}")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)

            # 1. Sauvegarde du MIDI
            midi_path = tmp_dir_path / "input.mid"
            with midi_path.open("wb") as f:
                shutil.copyfileobj(midi_file.file, f)

            # 2. Résolution du soundfont
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

            # 3. Rendu MIDI -> WAV
            raw_wav_path = tmp_dir_path / "01_raw.wav"
            render_midi_to_wav(str(midi_path), str(soundfont_path), str(raw_wav_path))

            # 4. Effets (reverb, filtres)
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

            # 5. Normalisation loudness
            normalized_wav_path = tmp_dir_path / "03_normalized.wav"
            normalize_loudness(str(fx_wav_path), str(normalized_wav_path), target_lufs=params.target_lufs)

            # 6. Export MP3
            mp3_path = tmp_dir_path / "output.mp3"
            export_to_mp3(str(normalized_wav_path), str(mp3_path))

            # 7. Copie hors du dossier temporaire pour la réponse
            final_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            shutil.copy(mp3_path, final_tmp.name)

    except HTTPException:
        raise
    except Exception as e:
        print("=== ERREUR PENDANT LA CONVERSION ===")
        traceback.print_exc()
        raise HTTPException(500, f"Erreur serveur pendant la conversion: {e}")

    return FileResponse(
        final_tmp.name,
        media_type="audio/mpeg",
        filename="conversion.mp3",
    )