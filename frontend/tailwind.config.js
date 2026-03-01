/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        nexus: {
          bg: '#0A0A0F',
          surface: '#111827',
          border: '#1F2937',
          accent: {
            yellow: '#F59E0B',
            blue: '#3B82F6',
            green: '#10B981',
            purple: '#8B5CF6',
            pink: '#EC4899',
            orange: '#F97316',
          },
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
