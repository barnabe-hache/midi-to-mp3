import numpy as np
import soundfile as sf
from pedalboard import Pedalboard, Reverb, HighpassFilter, LowpassFilter


def apply_effects(
    input_wav_path: str,
    output_wav_path: str,
    room_size: float = 0.5,      # 0.0 (sec) à 1.0 (grande salle)
    damping: float = 0.5,        # absorption des hautes fréquences dans la reverb
    wet_level: float = 0.3,      # proportion de signal "traité" (reverb)
    dry_level: float = 0.7,      # proportion de signal "brut"
    highpass_freq: float | None = None,   # ex: 80.0 pour couper les basses fréquences parasites
    lowpass_freq: float | None = None,    # ex: 12000.0 pour adoucir les aigus
) -> None:
    """
    Applique reverb + filtres sur un WAV, écrit le résultat dans output_wav_path.
    """
    audio, sample_rate = sf.read(input_wav_path)

    # pedalboard attend un array (channels, samples) si stéréo, ou (samples,) si mono
    if audio.ndim == 2:
        audio = audio.T  # soundfile renvoie (samples, channels), pedalboard veut (channels, samples)

    effects = [
        Reverb(
            room_size=room_size,
            damping=damping,
            wet_level=wet_level,
            dry_level=dry_level,
        )
    ]

    if highpass_freq:
        effects.append(HighpassFilter(cutoff_frequency_hz=highpass_freq))
    if lowpass_freq:
        effects.append(LowpassFilter(cutoff_frequency_hz=lowpass_freq))

    board = Pedalboard(effects)
    processed = board(audio, sample_rate)

    if processed.ndim == 2:
        processed = processed.T  # on repasse en (samples, channels) pour soundfile

    sf.write(output_wav_path, processed, sample_rate)