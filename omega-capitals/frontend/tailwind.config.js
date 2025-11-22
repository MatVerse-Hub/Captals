/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        omega: {
          green: '#00ff00',
          dark: '#0a0e0a',
          gray: '#1a1f1a'
        }
      }
    },
  },
  plugins: [],
}
