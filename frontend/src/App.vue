<script setup lang="ts">
import { ref, computed } from 'vue'
import AppHeader from './components/AppHeader.vue'
import MidiDropzone from './components/MidiDropzone.vue'
import PianoSelector from './components/PianoSelector.vue'
import EffectsPanel from './components/EffectsPanel.vue'
import ConversionProgress from './components/ConversionProgress.vue'
import ResultPlayer from './components/ResultPlayer.vue'
import type { SelectedPiano, EffectsParams, ConversionStatus } from './types'
import { convertMidiToMp3, previewSoundfont } from './composables/useApi'

// --- État du fichier MIDI et du piano ---
const midiFile = ref<File | null>(null)
const selectedPiano = ref<SelectedPiano | null>(null)
const effectsParams = ref<EffectsParams | null>(null)

// --- État de la conversion finale ---
const status = ref<ConversionStatus>('idle')
const phase = ref<'uploading' | 'processing'>('uploading')
const uploadPercent = ref(0)
const resultUrl = ref<string | null>(null)
const conversionError = ref<string | null>(null)

// --- État de l'écoute "Play sample with these effects" ---
const effectsPreviewPlaying = ref(false)
const effectsPreviewError = ref<string | null>(null)

const canConvert = computed(() =>
  midiFile.value !== null && selectedPiano.value !== null && status.value !== 'converting'
)

function onFileSelected(file: File) {
  midiFile.value = file
  resultUrl.value = null
  status.value = 'idle'
}

function onPianoSelected(piano: SelectedPiano) {
  selectedPiano.value = piano
}

function onParamsChanged(params: EffectsParams) {
  effectsParams.value = params
}

async function playEffectsSample() {
  if (!selectedPiano.value || !effectsParams.value) return
  effectsPreviewError.value = null
  effectsPreviewPlaying.value = true
  try {
    const url = await previewSoundfont({
      soundfontId: selectedPiano.value.presetId,
      customFile: selectedPiano.value.customFile,
      effectsParams: effectsParams.value,
    })
    const audio = new Audio(url)
    audio.play()
    audio.onended = () => {
      effectsPreviewPlaying.value = false
    }
  } catch (e) {
    effectsPreviewError.value = 'Could not play the sample'
    effectsPreviewPlaying.value = false
  }
}

async function startConversion() {
  if (!midiFile.value || !selectedPiano.value || !effectsParams.value) return

  status.value = 'converting'
  phase.value = 'uploading'
  uploadPercent.value = 0
  conversionError.value = null
  resultUrl.value = null

  try {
    const url = await convertMidiToMp3({
      midiFile: midiFile.value,
      soundfontId: selectedPiano.value.presetId,
      customSoundfont: selectedPiano.value.customFile,
      effectsParams: effectsParams.value,
      onUploadProgress: (percent) => {
        uploadPercent.value = percent
        if (percent >= 100) phase.value = 'processing'
      },
    })
    resultUrl.value = url
    status.value = 'done'
  } catch (e) {
    conversionError.value = e instanceof Error ? e.message : 'Conversion failed'
    status.value = 'error'
  }
}
</script>

<template>
  <AppHeader />
  <main>
    <h1>MIDI to MP3</h1>
    <p class="subtitle">
      Turn your MIDI file into an MP3 with a natural piano sound and the effects you choose.
    </p>

    <MidiDropzone @file-selected="onFileSelected" />
    <PianoSelector @piano-selected="onPianoSelected" />
    <EffectsPanel @params-changed="onParamsChanged" />

    <button
      class="preview-effects-btn"
      :disabled="!selectedPiano || effectsPreviewPlaying"
      @click="playEffectsSample"
    >
      {{ effectsPreviewPlaying ? 'Playing...' : 'Play sample with these effects' }}
    </button>
    <p v-if="effectsPreviewError" class="error-banner">{{ effectsPreviewError }}</p>

    <button class="convert-btn" :disabled="!canConvert" @click="startConversion">
      {{ status === 'converting' ? 'Converting...' : 'Convert to MP3' }}
    </button>

    <ConversionProgress
      v-if="status === 'converting'"
      :phase="phase"
      :upload-percent="uploadPercent"
    />

    <p v-if="status === 'error'" class="error-banner">{{ conversionError }}</p>

    <ResultPlayer v-if="status === 'done' && resultUrl" :audio-url="resultUrl" />
  </main>
</template>

<style scoped>
.subtitle {
  color: var(--color-ink-muted);
  margin-bottom: 2rem;
}

.preview-effects-btn {
  display: block;
  width: 100%;
  margin-top: 1rem;
  background: none;
  border: 1px solid var(--color-signal);
  color: var(--color-signal);
  border-radius: var(--radius-sm);
  padding: 0.6rem;
  font-size: 0.88rem;
  font-weight: 500;
}

.preview-effects-btn:hover:not(:disabled) {
  background: var(--color-signal-soft);
}

.preview-effects-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.convert-btn {
  display: block;
  width: 100%;
  margin-top: 1rem;
  background: var(--color-ink);
  color: var(--color-surface);
  border: none;
  border-radius: var(--radius-sm);
  padding: 0.9rem;
  font-size: 0.95rem;
  font-weight: 500;
}

.convert-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.convert-btn:disabled {
  background: var(--color-border);
  color: var(--color-ink-muted);
  cursor: not-allowed;
}

.error-banner {
  margin-top: 1.2rem;
  background: var(--color-alert-soft);
  color: var(--color-alert);
  border-radius: var(--radius-sm);
  padding: 0.8rem 1rem;
  font-size: 0.88rem;
}
</style>