import numpy as np
import soundfile as sf
from pedalboard import Pedalboard, Reverb, HighpassFilter, LowpassFilter, Compressor


def apply_effects(
    input_wav_path: str,
    output_wav_path: str,
    room_size: float = 0.5,
    damping: float = 0.5,
    wet_level: float = 0.3,
    dry_level: float = 0.7,
    highpass_freq: float | None = None,
    lowpass_freq: float | None = None,
    compression_amount: float = 0.0,
) -> None:
    """
    Applique compression + reverb + filtres sur un WAV, écrit le résultat dans output_wav_path.
    """
    audio, sample_rate = sf.read(input_wav_path)

    if audio.ndim == 2:
        audio = audio.T

    effects = []

    # Compression en premier dans la chaîne : elle égalise la dynamique
    # avant que la reverb ne soit ajoutée par-dessus.
    if compression_amount > 0:
        threshold_db = -10 - 30 * compression_amount   # de -10 dB à -40 dB
        ratio = 1 + 3 * compression_amount              # de 1:1 à 4:1
        effects.append(Compressor(threshold_db=threshold_db, ratio=ratio))

    effects.append(
        Reverb(
            room_size=room_size,
            damping=damping,
            wet_level=wet_level,
            dry_level=dry_level,
        )
    )

    if highpass_freq:
        effects.append(HighpassFilter(cutoff_frequency_hz=highpass_freq))
    if lowpass_freq:
        effects.append(LowpassFilter(cutoff_frequency_hz=lowpass_freq))

    board = Pedalboard(effects)
    processed = board(audio, sample_rate)

    if processed.ndim == 2:
        processed = processed.T

    sf.write(output_wav_path, processed, sample_rate)