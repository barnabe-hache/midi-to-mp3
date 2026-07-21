<script setup lang="ts">
defineProps<{
  audioUrl: string
}>()
</script>

<template>
  <section class="result">
    <h2 class="section-title">Your track</h2>
    <audio :src="audioUrl" controls class="result__player"></audio>
    <a :href="audioUrl" download="conversion.mp3" class="result__download">
      Download MP3
    </a>
    <p class="result__limit-note">Free plan: up to 10 conversions per day.</p>
  </section>
</template>

<style scoped>
.result {
  margin-top: 2.5rem;
  background: var(--color-signal-soft);
  border: 1px solid var(--color-signal);
  border-radius: var(--radius-md);
  padding: 1.2rem;
}

.section-title {
  font-size: 1rem;
  margin-bottom: 0.9rem;
}

.result__player {
  width: 100%;
  margin-bottom: 0.9rem;
}

.result__download {
  display: inline-block;
  background: var(--color-signal);
  color: var(--color-surface);
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 500;
  padding: 0.55rem 1.1rem;
  border-radius: var(--radius-sm);
}

.result__download:hover {
  opacity: 0.9;
}

.result__limit-note {
  margin-top: 0.8rem;
  font-size: 0.78rem;
  color: var(--color-ink-muted);
}
</style>