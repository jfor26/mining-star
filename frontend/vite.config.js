import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Configuracion de Vite para el front-end de Mining Star.
// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // En desarrollo, las peticiones a /api se reenvian al servidor Django.
    // Asi el navegador ve un solo origen y no hace falta habilitar CORS.
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/setupTests.js',
    globals: true,
  },
})
