import subprocess
from pathlib import Path

SAMPLE_RATE = 44100

def render_midi_to_wav(midi_path: str, soundfont_path: str, output_wav_path: str) -> None:
    """
    Rend un fichier MIDI en WAV via le binaire fluidsynth (mode non-interactif).
    """
    command = [
        "fluidsynth",
        "-ni",
        "-F", output_wav_path,
        "-r", str(SAMPLE_RATE),
        "-o", "audio.file.format=s16",   # PCM 16 bits, compatible avec tous les lecteurs
        soundfont_path,
        midi_path,
    ]

    print("=== Commande FluidSynth ===")
    print(" ".join(command))

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    print("=== STDOUT ===")
    print(result.stdout)
    print("=== STDERR ===")
    print(result.stderr)
    print(f"=== Return code: {result.returncode} ===")

    if result.returncode != 0:
        raise RuntimeError(f"Erreur FluidSynth (code {result.returncode}): {result.stderr}")

    if not Path(output_wav_path).exists():
        raise RuntimeError(
            f"FluidSynth s'est terminé sans erreur mais n'a pas créé le fichier de sortie.\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )