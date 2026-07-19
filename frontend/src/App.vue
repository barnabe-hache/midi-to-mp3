<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { checkBackendHealth } from './composables/useApi'

const backendReady = ref<boolean | null>(null)

onMounted(async () => {
  backendReady.value = await checkBackendHealth()
})
</script>

<template>
  <main>
    <h1>MIDI → MP3</h1>
    <p v-if="backendReady === null">Connexion au serveur...</p>
    <p v-else-if="backendReady">✅ Backend connecté</p>
    <p v-else>❌ Backend injoignable — vérifie qu'il tourne sur le port 8000</p>
  </main>
</template>