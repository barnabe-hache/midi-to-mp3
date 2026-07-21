<script setup lang="ts">
defineProps<{
  phase: 'uploading' | 'processing'
  uploadPercent: number
}>()
</script>

<template>
  <div class="progress">
    <div class="progress__bar-track">
      <div
        class="progress__bar-fill"
        :class="{ 'progress__bar-fill--indeterminate': phase === 'processing' }"
        :style="phase === 'uploading' ? { width: uploadPercent + '%' } : {}"
      ></div>
    </div>
    <p class="progress__label">
      {{ phase === 'uploading' ? `Uploading... ${uploadPercent}%` : 'Rendering piano, applying effects and normalizing...' }}
    </p>
  </div>
</template>

<style scoped>
.progress {
  margin-top: 2rem;
}

.progress__bar-track {
  width: 100%;
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
}

.progress__bar-fill {
  height: 100%;
  background: var(--gradient-signal);
  border-radius: 3px;
  transition: width 0.2s ease;
}

.progress__bar-fill--indeterminate {
  width: 40%;
  animation: indeterminate 1.2s ease-in-out infinite;
}

@keyframes indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(250%); }
}

.progress__label {
  margin-top: 0.6rem;
  font-size: 0.85rem;
  color: var(--color-ink-muted);
}
</style>