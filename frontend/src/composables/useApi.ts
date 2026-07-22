import type { Soundfont, EffectsParams } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    if (!response.ok) return false
    const data = await response.json()
    return data.status === 'ok'
  } catch (error) {
    console.error('Backend unreachable:', error)
    return false
  }
}

export async function fetchSoundfonts(): Promise<Soundfont[]> {
  const response = await fetch(`${API_BASE_URL}/soundfonts`)
  if (!response.ok) throw new Error('Failed to load piano list')
  const data = await response.json()
  return data.soundfonts
}

export async function previewSoundfont(params: {
  soundfontId?: string
  customFile?: File
  effectsParams?: EffectsParams
}): Promise<string> {
  const formData = new FormData()
  if (params.customFile) {
    formData.append('custom_soundfont', params.customFile)
  } else if (params.soundfontId) {
    formData.append('soundfont_id', params.soundfontId)
  } else {
    throw new Error('No soundfont specified')
  }
  if (params.effectsParams) {
    formData.append('effects_params', JSON.stringify(params.effectsParams))
  }

  const response = await fetch(`${API_BASE_URL}/preview`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || 'Preview failed')
  }
  const blob = await response.blob()
  return URL.createObjectURL(blob)
}

export { API_BASE_URL }


export function convertMidiToMp3(params: {
  midiFile: File
  soundfontId?: string
  customSoundfont?: File
  effectsParams: EffectsParams
  onUploadProgress: (percent: number) => void
}): Promise<string> {
  return new Promise((resolve, reject) => {
    const formData = new FormData()
    formData.append('midi_file', params.midiFile)
    if (params.customSoundfont) {
      formData.append('custom_soundfont', params.customSoundfont)
    } else if (params.soundfontId) {
      formData.append('soundfont_id', params.soundfontId)
    } else {
      reject(new Error('No piano selected'))
      return
    }
    formData.append('effects_params', JSON.stringify(params.effectsParams))

    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE_URL}/convert`)
    xhr.responseType = 'blob'

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        params.onUploadProgress(Math.round((event.loaded / event.total) * 100))
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        const url = URL.createObjectURL(xhr.response)
        resolve(url)
      } else {
        // La réponse d'erreur arrive aussi en blob à cause de responseType,
        // il faut la relire comme texte pour récupérer le message JSON du backend
        const reader = new FileReader()
        reader.onload = () => {
          try {
            const parsed = JSON.parse(reader.result as string)
            reject(new Error(parsed.detail || 'Conversion failed'))
          } catch {
            reject(new Error('Conversion failed'))
          }
        }
        reader.readAsText(xhr.response)
      }
    }

    xhr.onerror = () => reject(new Error('Network error during conversion'))

    xhr.send(formData)
  })
}