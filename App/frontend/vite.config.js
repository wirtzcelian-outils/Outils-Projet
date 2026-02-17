import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuration de Vite (outil de build)
export default defineConfig({
  plugins: [react()],
  server: {
    // Permet d'exposer le serveur sur le réseau local (utile pour Docker)
    host: true,
    port: 3000,
    // Configuration du proxy pour rediriger les requêtes API vers le backend Flask
    // Évite les problèmes de CORS en développement -> /api/... sera redirigé vers http://localhost:5000/api/...
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
