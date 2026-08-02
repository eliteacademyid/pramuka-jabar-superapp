/**
 * Error handling utilities for API calls and store actions.
 * Task 6.6 — centralised error handling for the dashboard store.
 */

/**
 * Extract a human-readable message from an Axios error or plain Error.
 * @param {unknown} err
 * @param {string} fallback
 * @returns {string}
 */
export function extractErrorMessage(err, fallback = 'Terjadi kesalahan. Silakan coba lagi.') {
  if (!err) return fallback

  // Axios HTTP error with FastAPI detail
  if (err?.response?.data?.detail) {
    const detail = err.response.data.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((d) => d.msg || d).join(', ')
  }

  // Axios network error
  if (err?.message === 'Network Error') {
    return 'Tidak dapat terhubung ke server. Periksa koneksi internet Anda.'
  }

  // Request timeout
  if (err?.code === 'ECONNABORTED') {
    return 'Permintaan timeout. Server mungkin sedang sibuk.'
  }

  // HTTP status messages
  if (err?.response?.status === 401) return 'Sesi Anda telah berakhir. Silakan login kembali.'
  if (err?.response?.status === 403) return 'Anda tidak memiliki izin untuk mengakses data ini.'
  if (err?.response?.status === 404) return 'Data tidak ditemukan.'
  if (err?.response?.status >= 500) return 'Terjadi kesalahan pada server. Silakan coba beberapa saat lagi.'

  return err?.message || fallback
}

/**
 * Log error to console in development only.
 * @param {string} context
 * @param {unknown} err
 */
export function logError(context, err) {
  if (import.meta.env.DEV) {
    console.error(`[${context}]`, err)
  }
}
