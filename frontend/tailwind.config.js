/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        pramuka: {
          50: '#f5fdf4',
          100: '#ebfbe8',
          500: '#3f7d20',
          600: '#2f5f17',
          700: '#274d13',
          900: '#18330d'
        },
        accent: {
          yellow: '#fbbf24'
        }
      },
      boxShadow: {
        soft: '0 10px 30px rgba(15, 23, 42, 0.08)'
      }
    }
  },
  plugins: []
}
