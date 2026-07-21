<script setup lang="ts">
</script>

<template>
  <header class="app-header">
    <div class="app-header__inner">
      <span class="app-header__logo-placeholder" aria-hidden="true"></span>
      <span class="app-header__title">MIDI Studio</span>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.app-header__inner {
  max-width: 760px;
  margin: 0 auto;
  padding: 1.1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.app-header__logo-placeholder {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: var(--color-signal);
  flex-shrink: 0;
}

.app-header__title {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
}
</style>