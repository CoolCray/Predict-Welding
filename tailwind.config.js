/** @type {import('tailwindcss').Config} */

const defaultTheme = require('tailwindcss/defaultTheme')
module.exports = {
  content: ['./components/*.{html,js}',
    './pages/**/*.{html,js}',
    './index.html'],
  theme: {
    extend: {
    },
    letterSpacing: {
      tightest: '-.075em',
      tighter: '-.05em',
      tight: '-.025em',
      normal: '0',
      wide: '.025em',
      wider: '.05em',
      widest: '1em',
    },
  },
  plugins: [],
}

