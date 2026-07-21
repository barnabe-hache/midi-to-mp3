<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Soundfont, SelectedPiano } from '../types'
import { fetchSoundfonts, previewSoundfont } from '../composables/useApi'

const emit = defineEmits<{
  'piano-selected': [piano: SelectedPiano]
}>()

const soundfonts = ref<Soundfont[]>([])
const selectedId = ref<string | null>(null)
const customFile = ref<File | null>(null)
const loadError = ref<string | null>(null)
const isLoading = ref(true)

const playingId = ref<string | null>(null)
const previewError = ref<string | null>(null)
let currentAudio: HTMLAudioElement | null = null

onMounted(async () => {
  try {
    soundfonts.value = await fetchSoundfonts()
  } catch (e) {
    loadError.value = 'Could not load the piano list. Is the server running?'
  } finally {
    isLoading.value = false
  }
})

function selectPreset(sf: Soundfont) {
  selectedId.value = sf.id
  customFile.value = null
  emit('piano-selected', { type: 'preset', presetId: sf.id, displayName: sf.name })
}

function onCustomFileChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.sf2')) {
    previewError.value = 'This file is not a .sf2 soundfont'
    return
  }
  customFile.value = file
  selectedId.value = null
  emit('piano-selected', { type: 'custom', customFile: file, displayName: file.name })
}

async function playSample(target: { id: string; soundfontId?: string; file?: File }) {
  previewError.value = null
  playingId.value = target.id
  try {
    const url = await previewSoundfont({
      soundfontId: target.soundfontId,
      customFile: target.file,
    })
    if (currentAudio) {
      currentAudio.pause()
    }
    currentAudio = new Audio(url)
    currentAudio.play()
    currentAudio.onended = () => {
      playingId.value = null
    }
  } catch (e) {
    previewError.value = 'Could not play this piano sample'
    playingId.value = null
  }
}
</script>

<template>
  <section class="piano-selector">
    <h2 class="section-title">Piano</h2>

    <p v-if="isLoading" class="muted">Loading pianos...</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <ul v-else class="piano-list">
      <li
        v-for="sf in soundfonts"
        :key="sf.id"
        class="piano-item"
        :class="{ 'piano-item--selected': selectedId === sf.id }"
      >
        <button class="piano-item__select" @click="selectPreset(sf)">
          {{ sf.name }}
        </button>
        <button
          class="piano-item__play"
          :disabled="playingId === sf.id"
          @click="playSample({ id: sf.id, soundfontId: sf.id })"
        >
          {{ playingId === sf.id ? 'Playing...' : 'Play sample' }}
        </button>
      </li>

      <li class="piano-item piano-item--custom" :class="{ 'piano-item--selected': !!customFile }">
        <label class="piano-item__select piano-item__select--file">
          {{ customFile ? customFile.name : 'Upload your own .sf2' }}
          <input type="file" accept=".sf2" @change="onCustomFileChange" hidden />
        </label>
        <button
          v-if="customFile"
          class="piano-item__play"
          :disabled="playingId === 'custom'"
          @click="playSample({ id: 'custom', file: customFile })"
        >
          {{ playingId === 'custom' ? 'Playing...' : 'Play sample' }}
        </button>
      </li>
    </ul>

    <p v-if="previewError" class="error">{{ previewError }}</p>
  </section>
</template>

<style scoped>
.piano-selector {
  margin-top: 2.5rem;
}

.section-title {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.muted {
  color: var(--color-ink-muted);
  font-size: 0.9rem;
}

.error {
  color: var(--color-alert);
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.piano-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.piano-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  padding: 0.7rem 0.9rem;
  transition: border-color 0.15s ease;
}

.piano-item--selected {
  border-color: var(--color-signal);
}

.piano-item__select {
  background: none;
  border: none;
  text-align: left;
  font-size: 0.92rem;
  font-weight: 500;
  color: var(--color-ink);
  flex: 1;
  cursor: pointer;
}

.piano-item__select--file {
  cursor: pointer;
  color: var(--color-ink-muted);
}

.piano-item--custom .piano-item__select {
  font-weight: 400;
}

.piano-item__play {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.35rem 0.7rem;
  font-size: 0.8rem;
  color: var(--color-signal);
  flex-shrink: 0;
}

.piano-item__play:hover:not(:disabled) {
  background: var(--color-signal-soft);
}

.piano-item__play:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>