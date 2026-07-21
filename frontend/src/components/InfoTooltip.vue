<script setup lang="ts">
defineProps<{
  text: string
}>()
</script>

<template>
  <span class="info-tooltip" tabindex="0">
    <span class="info-tooltip__icon" aria-hidden="true">?</span>
    <span class="info-tooltip__bubble" role="tooltip">{{ text }}</span>
  </span>
</template>

<style scoped>
.info-tooltip {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-signal-soft);
  color: var(--color-signal);
  font-size: 0.68rem;
  font-family: var(--font-body);
  font-weight: 600;
  cursor: default;
  margin-left: 0.4rem;
  transition: background-color 0.15s ease;
}

.info-tooltip:hover {
  background: var(--color-signal);
  color: #fff;
}

.info-tooltip__bubble {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  width: 220px;
  background: var(--color-ink);
  color: var(--color-surface);
  font-size: 0.78rem;
  font-weight: 400;
  line-height: 1.4;
  padding: 0.6rem 0.7rem;
  border-radius: var(--radius-sm);
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.12s ease;
  pointer-events: none;
  z-index: 10;
}

.info-tooltip:hover .info-tooltip__bubble,
.info-tooltip:focus-visible .info-tooltip__bubble {
  opacity: 1;
  visibility: visible;
}
</style>