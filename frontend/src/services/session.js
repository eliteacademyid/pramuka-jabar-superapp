import api from './api'

const KEY = 'javascout_me'

export async function fetchMe(force = false) {
  const cached = localStorage.getItem(KEY)
  if (cached && !force) {
    try {
      return JSON.parse(cached)
    } catch {
      /* fallthrough */
    }
  }
  const { data } = await api.get('/auth/me')
  localStorage.setItem(KEY, JSON.stringify(data))
  return data
}

export function clearSession() {
  localStorage.removeItem('token')
  localStorage.removeItem(KEY)
}

export function meFromCache() {
  try {
    return JSON.parse(localStorage.getItem(KEY))
  } catch {
    return null
  }
}

export function isAdmin(me) {
  return me && (me.user.role === 'admin' || me.user.role === 'staff')
}

export function hasActiveStore(me) {
  return me && me.store && me.store.status === 'active'
}
