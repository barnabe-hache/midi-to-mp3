<script setup lang="ts">
defineProps<{
  audioUrl: string
  downloadFilename: string
}>()
</script>

<template>
  <section class="result">
    <h2 class="section-title">Your track</h2>
    <audio :src="audioUrl" controls class="result__player"></audio>
    <a :href="audioUrl" :download="downloadFilename" class="result__download">
      Download MP3
    </a>
    <p class="result__limit-note">Free plan: up to 10 conversions per day.</p>
  </section>
</template>

<style scoped>
.result {
  margin-top: 2.5rem;
  background: var(--color-signal-soft);
  border: 1.5px solid var(--color-signal);
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
  background: var(--gradient-signal);
  color: #fff;
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 500;
  padding: 0.6rem 1.2rem;
  border-radius: var(--radius-sm);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.result__download:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(47, 111, 94, 0.28);
}

.result__limit-note {
  margin-top: 0.8rem;
  font-size: 0.78rem;
  color: var(--color-ink-muted);
}
</style>