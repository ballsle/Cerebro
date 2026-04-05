/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
      },
      colors: {
        surface: {
          900: '#0f0f13',
          800: '#16161d',
          700: '#1e1e28',
          600: '#2a2a36',
        },
        navy: {
          400: '#6b8cce',
          500: '#4a6fa5',
          600: '#3a5a8a',
        },
      },
    },
  },
  plugins: [],
};
