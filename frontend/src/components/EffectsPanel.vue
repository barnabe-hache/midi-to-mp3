<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { DEFAULT_EFFECTS_PARAMS, type EffectsParams } from '../types'
import InfoTooltip from './InfoTooltip.vue'

const emit = defineEmits<{
  'params-changed': [params: EffectsParams]
}>()

const params = reactive<EffectsParams>({ ...DEFAULT_EFFECTS_PARAMS })
const highpassEnabled = ref(false)
const lowpassEnabled = ref(false)

// Valeurs par défaut utilisées quand on active un filtre pour la première fois
const DEFAULT_HIGHPASS = 80
const DEFAULT_LOWPASS = 12000

watch(highpassEnabled, (enabled) => {
  params.highpass_freq = enabled ? DEFAULT_HIGHPASS : null
})
watch(lowpassEnabled, (enabled) => {
  params.lowpass_freq = enabled ? DEFAULT_LOWPASS : null
})

watch(
  params,
  () => emit('params-changed', { ...params }),
  { deep: true, immediate: true }
)

function resetToDefaults() {
  Object.assign(params, DEFAULT_EFFECTS_PARAMS)
  highpassEnabled.value = false
  lowpassEnabled.value = false
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

watch(() => params.room_size, (v) => {
  const clamped = clamp(v, 0, 1)
  if (clamped !== v) params.room_size = clamped
})
watch(() => params.wet_level, (v) => {
  const clamped = clamp(v, 0, 1)
  if (clamped !== v) params.wet_level = clamped
})
watch(() => params.damping, (v) => {
  const clamped = clamp(v, 0, 1)
  if (clamped !== v) params.damping = clamped
})
watch(() => params.highpass_freq, (v) => {
  if (v === null) return
  const clamped = clamp(v, 20, 500)
  if (clamped !== v) params.highpass_freq = clamped
})
watch(() => params.lowpass_freq, (v) => {
  if (v === null) return
  const clamped = clamp(v, 2000, 18000)
  if (clamped !== v) params.lowpass_freq = clamped
})
watch(() => params.compression_amount, (v) => {
  const clamped = clamp(v, 0, 1)
  if (clamped !== v) params.compression_amount = clamped
})

</script>

<template>
  <section class="effects-panel">
    <div class="effects-panel__header">
      <h2 class="section-title">Sound effects</h2>
      <button class="reset-btn" @click="resetToDefaults">Reset to defaults</button>
    </div>

    <!-- Reverb -->
    <div class="effect-group">
      <p class="effect-group__title">Reverb</p>

      <div class="slider-row">
        <label class="slider-label">
          Room size
          <InfoTooltip text="How large the virtual room feels. Turn it up for a big hall sound, down for a small, tight room. Range: 0.00 (very small) to 1.00 (very large)." />
        </label>
        <input type="range" min="0" max="1" step="0.01" v-model.number="params.room_size" />
        <input
          type="number"
          class="value-input"
          min="0" max="1" step="0.01"
          v-model.number="params.room_size"
        />
      </div>

      <div class="slider-row">
        <label class="slider-label">
          Reverb amount
          <InfoTooltip text="How much reverb is mixed into the sound. Turn it up for a more spacious, ambient feel, down for a drier, more direct sound. Range: 0.00 (dry) to 1.00 (fully wet)." />
        </label>
        <input type="range" min="0" max="1" step="0.01" v-model.number="params.wet_level" />
        <input
          type="number"
          class="value-input"
          min="0" max="1" step="0.01"
          v-model.number="params.wet_level"
        />
      </div>

      <div class="slider-row">
        <label class="slider-label">
          Damping
          <InfoTooltip text="How quickly high frequencies fade in the reverb tail. Turn it up for a darker, softer reverb, down for a brighter, more open one. Range: 0.00 (bright) to 1.00 (dark)." />
        </label>
        <input type="range" min="0" max="1" step="0.01" v-model.number="params.damping" />
        <input
          type="number"
          class="value-input"
          min="0" max="1" step="0.01"
          v-model.number="params.damping"
        />
      </div>
    </div>

    <!-- Filtres -->
    <div class="effect-group">
      <p class="effect-group__title">Tone filters</p>

      <div class="toggle-row">
        <label class="toggle-label">
          <input type="checkbox" v-model="highpassEnabled" />
          Cut low frequencies
          <InfoTooltip text="Removes rumble and muddiness in the low end. Raise the frequency to cut more bass, lower it to keep more warmth. Range: 20 Hz to 500 Hz." />
        </label>
        <template v-if="highpassEnabled">
          <input type="range" min="20" max="500" step="1" v-model.number="params.highpass_freq" />
          <input
            type="number"
            class="value-input value-input--wide"
            min="20" max="500" step="1"
            v-model.number="params.highpass_freq"
          />
          <span class="unit">Hz</span>
        </template>
      </div>

      <div class="toggle-row">
        <label class="toggle-label">
          <input type="checkbox" v-model="lowpassEnabled" />
          Cut high frequencies
          <InfoTooltip text="Softens harsh or bright high end. Lower the frequency for a warmer, more muffled sound, raise it to keep more brightness. Range: 2000 Hz to 18000 Hz." />
        </label>
        <template v-if="lowpassEnabled">
          <input type="range" min="2000" max="18000" step="100" v-model.number="params.lowpass_freq" />
          <input
            type="number"
            class="value-input value-input--wide"
            min="2000" max="18000" step="100"
            v-model.number="params.lowpass_freq"
          />
          <span class="unit">Hz</span>
        </template>
      </div>
    </div>
    <!-- Dynamics -->
    <div class="effect-group">
      <p class="effect-group__title">Dynamics</p>

      <div class="slider-row">
        <label class="slider-label">
          Compression
          <InfoTooltip text="Evens out loud and quiet notes for a more consistent, polished sound. Turn it up for a tighter, more controlled sound, down to keep the natural dynamics of your playing. Range: 0.00 (off) to 1.00 (strong)." />
        </label>
        <input type="range" min="0" max="1" step="0.01" v-model.number="params.compression_amount" />
        <input
          type="number"
          class="value-input"
          min="0" max="1" step="0.01"
          v-model.number="params.compression_amount"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.effects-panel {
  margin-top: 2.5rem;
}

.effects-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
}

.section-title {
  font-size: 1rem;
}

.reset-btn {
  background: none;
  border: none;
  color: var(--color-ink-muted);
  font-size: 0.8rem;
  text-decoration: underline;
}

.reset-btn:hover {
  color: var(--color-signal);
}

.effect-group {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.1rem 1.2rem;
  margin-bottom: 1rem;
  transition: box-shadow 0.15s ease;
}

.effect-group:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
}

.effect-group__title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-signal);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.9rem;
}

.slider-row {
  display: grid;
  grid-template-columns: 160px 1fr 60px;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 0.7rem;
}

.slider-row:last-child {
  margin-bottom: 0;
}

.slider-label {
  display: flex;
  align-items: center;
  font-size: 0.88rem;
}

.value-input {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--color-ink);
  text-align: right;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.2rem 0.4rem;
  width: 100%;
  transition: border-color 0.15s ease;
}

.value-input:focus-visible {
  border-color: var(--color-signal);
}

.value-input--wide {
  width: 70px;
  flex-shrink: 0;
}

.unit {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--color-ink-muted);
}

input[type='range'] {
  accent-color: var(--color-signal);
}

.toggle-row {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 0.7rem;
}

.toggle-row:last-child {
  margin-bottom: 0;
}

.toggle-label {
  display: flex;
  align-items: center;
  font-size: 0.88rem;
  gap: 0.5rem;
  flex-shrink: 0;
  min-width: 190px;
}

.toggle-row input[type='range'] {
  flex: 1;
}
</style>