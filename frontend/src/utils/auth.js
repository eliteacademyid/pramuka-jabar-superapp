/**
 * Auth utility helpers
 * Used by router guards, components, and tests to verify login flow.
 */
import { jwtDecode } from 'jwt-decode'

/**
 * Check whether a JWT token string is still valid (not expired).
 * @param {string} token
 * @returns {boolean}
 */
export function isTokenValid(token) {
  if (!token) return false
  try {
    const { exp } = jwtDecode(token)
    if (!exp) return true // no expiry claim → treat as valid
    return Date.now() < exp * 1000
  } catch {
    return false
  }
}

/**
 * Decode token payload without throwing.
 * @param {string} token
 * @returns {object|null}
 */
export function decodeToken(token) {
  if (!token) return null
  try {
    return jwtDecode(token)
  } catch {
    return null
  }
}

/**
 * Get stored token from localStorage.
 * @returns {string|null}
 */
export function getStoredToken() {
  return localStorage.getItem('token') || null
}

/**
 * Get stored user from localStorage.
 * @returns {object|null}
 */
export function getStoredUser() {
  try {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

/**
 * Clear all auth data from localStorage.
 */
export function clearAuthStorage() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}
