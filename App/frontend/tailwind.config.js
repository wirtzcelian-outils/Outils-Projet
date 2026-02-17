/** @type {import('tailwindcss').Config} */
export default {
  // Indique à Tailwind quels fichiers scanner pour générer le CSS
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Extension de la palette de couleurs par défaut
      colors: {
        background: '#0f172a', // Bleu nuit très sombre
        surface: '#1e293b',    // Bleu gris foncé
        primary: '#3b82f6',    // Bleu vif système
        secondary: '#64748b',  // Gris ardoise
        accent: '#8b5cf6',     // Violet
      },
      // Ajout de la police Inter
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
