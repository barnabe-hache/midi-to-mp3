import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from pedalboard import Pedalboard, Limiter

TARGET_LUFS = -14.0


def normalize_loudness(
    input_wav_path: str,
    output_wav_path: str,
    target_lufs: float = TARGET_LUFS,
) -> None:
    """
    Normalise le volume perçu (loudness) selon la norme LUFS,
    puis applique un limiteur pour éviter tout écrêtage audible.
    """
    audio, sample_rate = sf.read(input_wav_path)

    meter = pyln.Meter(sample_rate)
    current_loudness = meter.integrated_loudness(audio)

    if current_loudness == float("-inf"):
        sf.write(output_wav_path, audio, sample_rate)
        return

    normalized_audio = pyln.normalize.loudness(audio, current_loudness, target_lufs)

    # Limiteur : lisse les pics résiduels sans écraser le son ni créer de distorsion,
    # contrairement à une simple division par le pic.
    if normalized_audio.ndim == 2:
        board_input = normalized_audio.T
    else:
        board_input = normalized_audio

    board = Pedalboard([Limiter(threshold_db=-1.0, release_ms=100)])
    limited = board(board_input, sample_rate)

    if limited.ndim == 2:
        limited = limited.T

    sf.write(output_wav_path, limited, sample_rate)