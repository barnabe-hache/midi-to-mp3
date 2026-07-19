const API_BASE_URL = 'http://localhost:8000'

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    if (!response.ok) return false
    const data = await response.json()
    return data.status === 'ok'
  } catch (error) {
    console.error('Backend injoignable :', error)
    return false
  }
}

export { API_BASE_URL }