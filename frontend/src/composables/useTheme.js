import { ref, onMounted, onBeforeUnmount } from 'vue'
import api from '../services/api'

const THEME_KEY = 'javascout-theme'
const VALID_THEMES = ['default', 'dark', 'blue']
const theme = ref(loadLocal())

function loadLocal() {
  try {
    const t = localStorage.getItem(THEME_KEY) || 'default'
    return VALID_THEMES.includes(t) ? t : 'default'
  } catch {
    return 'default'
  }
}

function apply(t) {
  theme.value = t
  try {
    localStorage.setItem(THEME_KEY, t)
  } catch { /* abaikan */ }
  const root = document.documentElement
  root.classList.remove('dark', 'blue')
  if (t !== 'default') root.classList.add(t)
}

async function setTheme(t, opts = {}) {
  const next = VALID_THEMES.includes(t) ? t : 'default'
  apply(next)
  if (opts.persist !== false && localStorage.getItem('token')) {
    try {
      await api.put('/me/theme', { theme: next })
    } catch { /* simpan lokal dulu, sinkron berikutnya */ }
  }
}

async function syncFromServer() {
  if (!localStorage.getItem('token')) return
  try {
    const { data } = await api.get('/me/theme')
    if (VALID_THEMES.includes(data.theme)) apply(data.theme)
  } catch { /* abaikan */ }
}

export function useTheme() {
  onMounted(syncFromServer)
  return { theme, setTheme }
}

export function initTheme() {
  apply(loadLocal())
}
