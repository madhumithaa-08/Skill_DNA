/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        craft: {
          indigo: {
            50: '#eef2ff',
            100: '#e0e7ff',
            500: '#6366f1',
            600: '#4f46e5',
            800: '#3730a3',
            900: '#1e1b4b',
            950: '#0f0c2e',
          },
          crimson: {
            50: '#fef2f2',
            100: '#fee2e2',
            500: '#ef4444',
            600: '#dc2626',
            700: '#b91c1c',
            800: '#991b1b',
            900: '#7f1d1d',
          },
          amber: {
            50: '#fffbeb',
            100: '#fef3c7',
            400: '#fbbf24',
            500: '#f59e0b',
            600: '#d97706',
            700: '#b45309',
          },
          parchment: {
            50: '#ffffff',
            100: '#fdfbf7',
            200: '#f7f4ed',
            300: '#ebe6db',
          },
          slate: {
            900: '#1e293b',
            950: '#0f172a',
          },
          silk: '#faf8f5',
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', '"Times New Roman"', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        'serif-heading': ['"Playfair Display"', 'Georgia', 'serif'],
      },
      boxShadow: {
        'craft': '0 4px 20px -2px rgba(30, 27, 75, 0.08), 0 2px 6px -1px rgba(30, 27, 75, 0.04)',
        'craft-hover': '0 10px 25px -3px rgba(30, 27, 75, 0.12), 0 4px 10px -2px rgba(30, 27, 75, 0.06)',
      },
    },
  },
  plugins: [],
}
