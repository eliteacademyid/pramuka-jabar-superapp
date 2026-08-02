import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFileSync } from 'node:fs'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    https: {
      key: readFileSync('./certs/localhost+2-key.pem'),
      cert: readFileSync('./certs/localhost+2.pem')
    }
  }
})
