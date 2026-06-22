/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'system-ui', 'sans-serif'],
      },
      colors: {
        navy: {
          50: '#e8eaf6',
          100: '#c5c9e8',
          200: '#9fa6d8',
          300: '#7883c8',
          400: '#5a67bc',
          500: '#3c4cb0',
          600: '#3645a8',
          700: '#2e3a9e',
          800: '#262f95',
          900: '#0a0f2e',
          950: '#060818',
        },
        crimson: {
          400: '#ff6b6b',
          500: '#ef4444',
          600: '#dc2626',
        },
        teal: {
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
        },
        amber: {
          400: '#fbbf24',
          500: '#f59e0b',
        },
        emerald: {
          400: '#34d399',
          500: '#10b981',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-hero': 'linear-gradient(135deg, #060818 0%, #0a0f2e 50%, #0d1a3a 100%)',
        'gradient-card': 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
        'gradient-risk-low': 'linear-gradient(135deg, #10b981, #34d399)',
        'gradient-risk-medium': 'linear-gradient(135deg, #f59e0b, #fbbf24)',
        'gradient-risk-high': 'linear-gradient(135deg, #ef4444, #ff6b6b)',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.1)',
        'glow-red': '0 0 30px rgba(239, 68, 68, 0.3)',
        'glow-green': '0 0 30px rgba(16, 185, 129, 0.3)',
        'glow-amber': '0 0 30px rgba(245, 158, 11, 0.3)',
        'glow-teal': '0 0 20px rgba(20, 184, 166, 0.4)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'heartbeat': 'heartbeat 1.5s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        heartbeat: {
          '0%, 100%': { transform: 'scale(1)' },
          '14%': { transform: 'scale(1.1)' },
          '28%': { transform: 'scale(1)' },
          '42%': { transform: 'scale(1.1)' },
          '70%': { transform: 'scale(1)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
