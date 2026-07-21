<script setup lang="ts">
import logoUrl from '../assets/logo.svg'
</script>

<template>
  <header class="app-header">
    <div class="app-header__inner">
      <a href="/" class="app-header__brand">
        <img :src="logoUrl" alt="Notewave logo" class="app-header__logo" />
        <span class="app-header__title">Notewave</span>
      </a>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(245, 245, 243, 0.7);
  backdrop-filter: blur(14px) saturate(160%);
  -webkit-backdrop-filter: blur(14px) saturate(160%);
  border-bottom: 1px solid var(--color-border);
  margin: 0 -1.5rem;
}

.app-header__inner {
  max-width: 760px;
  margin: 0 auto;
  padding: 0.9rem 1.5rem;
  display: flex;
  align-items: center;
}

.app-header__brand {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  text-decoration: none;
  color: var(--color-ink);
}

.app-header__logo {
  width: 24px;
  height: 24px;
}

.app-header__title {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 1.05rem;
}
</style>