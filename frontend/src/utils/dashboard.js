/**
 * Dashboard utility helpers
 * Used by dashboard store and components to normalise API responses.
 */

/**
 * Normalise perbandingan API response — supports both array and
 * object-with-items shapes returned by different API versions.
 * @param {unknown} data - Raw API response data
 * @returns {Array}
 */
export function normalisePerbandingan(data) {
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.items)) return data.items
  if (data && Array.isArray(data.data)) return data.data
  return []
}

/**
 * Normalise statistik response with safe fallback values.
 * @param {Object} data
 * @returns {Object}
 */
export function normaliseStatistik(data) {
  return {
    total_program: data?.total_program ?? 0,
    total_kegiatan: data?.total_kegiatan ?? 0,
    program_berjalan: data?.program_berjalan ?? 0,
    program_selesai: data?.program_selesai ?? 0,
    menunggu_approval: data?.menunggu_approval ?? 0,
    total_anggaran: data?.total_anggaran ?? 0,
    realisasi_anggaran: data?.realisasi_anggaran ?? 0,
    persentase_capaian: data?.persentase_capaian ?? '0%'
  }
}

/**
 * Format rupiah value for display.
 * @param {number} value
 * @returns {string}
 */
export function formatRupiah(value) {
  if (!value && value !== 0) return '-'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value)
}
