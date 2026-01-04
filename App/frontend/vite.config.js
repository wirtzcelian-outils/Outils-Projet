import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Local backend
        changeOrigin: true,
        // For docker, we use nginx, so this is just for npm run dev
      }
    }
  }
})
