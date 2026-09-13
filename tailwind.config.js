/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        bio: {
          50: '#eefdf3',
          100: '#d7f9e3',
          200: '#b2f1ca',
          300: '#7ee5aa',
          400: '#45d183',
          500: '#1eb866',
          600: '#119652',
          700: '#107844',
          800: '#125f39',
          900: '#104e30',
          950: '#082b1b',
        },
      },
    },
  },
  plugins: [],
}
