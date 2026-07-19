from pydub import AudioSegment


def export_to_mp3(input_wav_path: str, output_mp3_path: str, bitrate: str = "320k") -> None:
    """
    Convertit un WAV en MP3 haute qualité (320kbps par défaut).
    """
    audio = AudioSegment.from_wav(input_wav_path)
    audio.export(output_mp3_path, format="mp3", bitrate=bitrate)