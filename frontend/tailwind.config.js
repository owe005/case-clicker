/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        yellow: '#f4c430',
        'gray-dark': '#2d2d2d',
        'gray-darker': '#1a1a1a',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        display: ['Clash Display', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 20px rgba(0, 0, 0, 0.025), 0 40px 100px -20px rgba(0, 0, 0, 0.3)',
        'glass': '0 0 20px rgba(244, 196, 48, 0.05), inset 0 0 20px rgba(244, 196, 48, 0.05)',
        'glass-hover': '0 0 30px rgba(244, 196, 48, 0.1), inset 0 0 30px rgba(244, 196, 48, 0.1)',
        'glass-strong': '0 0 40px rgba(244, 196, 48, 0.15), inset 0 0 40px rgba(244, 196, 48, 0.15)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-dots': "url(\"data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%232d2d2d' fill-opacity='0.3' fill-rule='evenodd'%3E%3Ccircle cx='3' cy='3' r='1'/%3E%3C/g%3E%3C/svg%3E\")",
        'gradient-mesh': "linear-gradient(to right, rgba(244, 196, 48, 0.025) 1px, transparent 1px), linear-gradient(to bottom, rgba(244, 196, 48, 0.025) 1px, transparent 1px)",
      },
      animation: {
        'shimmer': 'shimmer 2.5s linear infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' }
        }
      }
    },
  },
  plugins: [],
}

