import mido
from pathlib import Path

mid = mido.MidiFile()
track = mido.MidiTrack()
mid.tracks.append(track)

track.append(mido.Message('program_change', program=0, time=0))

notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
for note in notes:
    track.append(mido.Message('note_on', note=note, velocity=80, time=0))
    track.append(mido.Message('note_off', note=note, velocity=80, time=240))

assets_dir = Path(__file__).parent / "app" / "assets"
assets_dir.mkdir(parents=True, exist_ok=True)
mid.save(assets_dir / "demo_scale.mid")
print("Demo MIDI file created at", assets_dir / "demo_scale.mid")