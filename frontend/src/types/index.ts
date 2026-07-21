export interface Soundfont {
  id: string
  name: string
}

export interface EffectsParams {
  room_size: number
  damping: number
  wet_level: number
  dry_level: number
  highpass_freq: number | null
  lowpass_freq: number | null
  target_lufs: number
}

export const DEFAULT_EFFECTS_PARAMS: EffectsParams = {
  room_size: 0.3,
  damping: 0.5,
  wet_level: 0.15,
  dry_level: 0.85,
  highpass_freq: null,
  lowpass_freq: null,
  compression_amount: 0.2,
  target_lufs: -14.0,
}

export type ConversionStatus = 'idle' | 'converting' | 'done' | 'error'

export interface SelectedPiano {
  type: 'preset' | 'custom'
  presetId?: string
  customFile?: File
  displayName: string
}


export interface EffectsParams {
  room_size: number
  damping: number
  wet_level: number
  dry_level: number
  highpass_freq: number | null
  lowpass_freq: number | null
  compression_amount: number
  target_lufs: number
}