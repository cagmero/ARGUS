/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        'neo-yellow': '#FFFF00',
        'neo-pink': '#FF00FF',
        'neo-cyan': '#00FFFF',
        'neo-green': '#00FF00',
        'neo-orange': '#FF8000',
        'neo-purple': '#8000FF',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Courier New', 'monospace'],
        'bold': ['Inter', 'Arial Black', 'sans-serif'],
      },
      boxShadow: {
        'brutal': '8px 8px 0px 0px #000000',
        'brutal-sm': '4px 4px 0px 0px #000000',
        'brutal-lg': '12px 12px 0px 0px #000000',
      },
    },
  },
  plugins: [],
}