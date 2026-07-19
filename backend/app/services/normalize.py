import numpy as np
import soundfile as sf
import pyloudnorm as pyln

# Cibles standard de l'industrie (LUFS intégré)
TARGET_LUFS = -14.0   # norme communément utilisée par Spotify, YouTube, Instagram


def normalize_loudness(
    input_wav_path: str,
    output_wav_path: str,
    target_lufs: float = TARGET_LUFS,
) -> None:
    """
    Normalise le volume perçu (loudness) selon la norme LUFS,
    pour une compatibilité optimale avec les plateformes de streaming.
    """
    audio, sample_rate = sf.read(input_wav_path)

    meter = pyln.Meter(sample_rate)
    current_loudness = meter.integrated_loudness(audio)

    # Si le fichier est un silence total, on évite une division par -inf
    if current_loudness == float("-inf"):
        sf.write(output_wav_path, audio, sample_rate)
        return

    normalized_audio = pyln.normalize.loudness(audio, current_loudness, target_lufs)

    # Sécurité anti-clipping : on s'assure qu'on ne dépasse pas [-1.0, 1.0]
    peak = np.max(np.abs(normalized_audio))
    if peak > 1.0:
        normalized_audio = normalized_audio / peak

    sf.write(output_wav_path, normalized_audio, sample_rate)