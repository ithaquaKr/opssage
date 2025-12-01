/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Claude UI Primary Colors
        primary: {
          DEFAULT: '#CC785C',
          hover: '#B86B50',
          light: '#FDF6F3',
        },
        // Neutral Scale
        gray: {
          50: '#F9F9F9',
          100: '#F3F3F3',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          900: '#171717',
        },
        // Semantic Colors
        success: '#16A34A',
        warning: '#EA580C',
        error: '#DC2626',
        info: '#2563EB',
        // Text Colors
        text: {
          primary: '#1F1F1F',
          secondary: '#666666',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
        mono: ['"SF Mono"', '"Monaco"', '"Inconsolata"', '"Fira Code"', '"Dank Mono"', 'monospace'],
      },
      fontSize: {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        '3xl': '1.875rem',
      },
      spacing: {
        1: '0.25rem',
        2: '0.5rem',
        3: '0.75rem',
        4: '1rem',
        5: '1.25rem',
        6: '1.5rem',
        8: '2rem',
        10: '2.5rem',
        12: '3rem',
        16: '4rem',
      },
      borderRadius: {
        sm: '0.25rem',
        DEFAULT: '0.5rem',
        md: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
        full: '9999px',
      },
      boxShadow: {
        sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
        DEFAULT: '0 1px 3px rgba(0, 0, 0, 0.05)',
        md: '0 2px 4px rgba(0, 0, 0, 0.08)',
        lg: '0 4px 12px rgba(0, 0, 0, 0.1)',
        xl: '0 8px 24px rgba(0, 0, 0, 0.12)',
        '2xl': '0 20px 50px rgba(0, 0, 0, 0.15)',
      },
    },
  },
  plugins: [],
}
