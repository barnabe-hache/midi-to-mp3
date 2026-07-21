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

const midiFile = ref<File | null>(null)
const selectedPiano = ref<SelectedPiano | null>(null)
const effectsParams = ref<EffectsParams | null>(null)

const status = ref<ConversionStatus>('idle')
const phase = ref<'uploading' | 'processing'>('uploading')
const uploadPercent = ref(0)
const resultUrl = ref<string | null>(null)
const conversionError = ref<string | null>(null)

const effectsPreviewPlaying = ref(false)
const effectsPreviewError = ref<string | null>(null)

const canConvert = computed(() =>
  midiFile.value !== null && selectedPiano.value !== null && status.value !== 'converting'
)

const downloadFilename = computed(() =>
  midiFile.value ? buildDownloadFilename(midiFile.value.name) : 'conversion_notewave.mp3'
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

function buildDownloadFilename(originalName: string): string {
  const nameWithoutExt = originalName.replace(/\.(mid|midi)$/i, '')
  return `${nameWithoutExt}_notewave.mp3`
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
  <div class="bg-blob bg-blob--1"></div>
  <div class="bg-blob bg-blob--2"></div>

  <AppHeader />
  <main>
    <div class="intro">
      <span class="intro__badge">🎹 No signup · Unlimited · Free</span>
      <h1>Convert your MIDI</h1>
      <p class="intro__subtitle">
        Pick a piano, tweak the effects, and export a track ready for Spotify, YouTube, or Instagram.
      </p>
    </div>

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

    <ResultPlayer
      v-if="status === 'done' && resultUrl"
      :audio-url="resultUrl"
      :download-filename="downloadFilename"
    />
  </main>
</template>

<style scoped>
.intro {
  text-align: center;
  padding: 3rem 0 2.5rem;
}

.intro__badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0.4rem 0.9rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-ink-muted);
  margin-bottom: 1.3rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.intro h1 {
  font-size: 2.1rem;
  margin-bottom: 0.7rem;
}

.intro__subtitle {
  color: var(--color-ink-muted);
  font-size: 1rem;
  max-width: 440px;
  margin: 0 auto;
}

.preview-effects-btn {
  display: block;
  width: 100%;
  margin-top: 1rem;
  background: none;
  border: 1px solid var(--color-signal);
  color: var(--color-signal);
  border-radius: var(--radius-sm);
  padding: 0.65rem;
  font-size: 0.88rem;
  font-weight: 500;
  transition: background-color 0.15s ease, transform 0.15s ease;
}

.preview-effects-btn:hover:not(:disabled) {
  background: var(--color-signal-soft);
  transform: translateY(-1px);
}

.preview-effects-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.convert-btn {
  display: block;
  width: 100%;
  margin-top: 1rem;
  background: var(--gradient-signal);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  padding: 0.95rem;
  font-size: 0.95rem;
  font-weight: 500;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.convert-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(47, 111, 94, 0.32);
}

.convert-btn:disabled {
  background: var(--color-border);
  color: var(--color-ink-muted);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
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