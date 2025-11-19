/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui'],
      },
      colors: {
        background: 'var(--color-background)',
        foreground: 'var(--color-foreground)',
        sidebar: 'var(--color-sidebar)',
        card: 'var(--color-card)',
        border: 'var(--color-border)',
        primary: {
          DEFAULT: 'var(--color-primary)',
          hover: 'var(--color-primary-hover)',
        },
        secondary: 'var(--color-secondary)',
        'accent-green': 'var(--color-accent-green)',
        'accent-yellow': 'var(--color-accent-yellow)',
        'accent-red': 'var(--color-accent-red)',
      },
      animation: {
        in: 'animate-in 0.6s ease-out',
      },
      keyframes: {
        'animate-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

module.exports = config;
