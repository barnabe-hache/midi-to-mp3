<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  'file-selected': [file: File]
}>()

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const errorMessage = ref<string | null>(null)

function isMidiFile(file: File): boolean {
  return /\.(mid|midi)$/i.test(file.name)
}

function handleFile(file: File) {
  if (!isMidiFile(file)) {
    errorMessage.value = 'This file is not a .mid or .midi'
    return
  }
  errorMessage.value = null
  selectedFile.value = file
  emit('file-selected', file)
}

function onDrop(event: DragEvent) {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) handleFile(file)
}

function onFileInputChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) handleFile(file)
}

function reset() {
  selectedFile.value = null
  errorMessage.value = null
}

defineExpose({ reset })
</script>

<template>
  <div
    class="dropzone"
    :class="{ 'dropzone--dragging': isDragging, 'dropzone--filled': selectedFile }"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="onDrop"
  >
    <template v-if="!selectedFile">
      <p class="dropzone__label">Drop your MIDI file here</p>
      <p class="dropzone__hint">or</p>
      <label class="dropzone__button">
        Choose a file
        <input type="file" accept=".mid,.midi" @change="onFileInputChange" hidden />
      </label>
    </template>

    <template v-else>
      <p class="dropzone__filename">{{ selectedFile.name }}</p>
      <button class="dropzone__replace" @click="reset">Change file</button>
    </template>

    <p v-if="errorMessage" class="dropzone__error">{{ errorMessage }}</p>
  </div>
</template>

<style scoped>
.dropzone {
  border: 1.5px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  padding: 2.5rem 1.5rem;
  text-align: center;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}

.dropzone--dragging {
  border-color: var(--color-signal);
  background: var(--color-signal-soft);
}

.dropzone--filled {
  border-style: solid;
  border-color: var(--color-signal);
}

.dropzone__label {
  font-weight: 500;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.dropzone__hint {
  color: var(--color-ink-muted);
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.dropzone__button {
  display: inline-block;
  border: 1px solid var(--color-ink);
  border-radius: var(--radius-sm);
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.dropzone__button:hover {
  background: var(--color-ink);
  color: var(--color-surface);
}

.dropzone__filename {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  word-break: break-all;
}

.dropzone__replace {
  background: none;
  border: none;
  color: var(--color-signal);
  font-size: 0.85rem;
  text-decoration: underline;
}

.dropzone__error {
  color: var(--color-alert);
  font-size: 0.85rem;
  margin-top: 0.75rem;
}
</style>