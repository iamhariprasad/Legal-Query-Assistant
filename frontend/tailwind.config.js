import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ink: '#111827',
        court: '#0f766e',
        brief: '#b45309',
        docket: '#2563eb',
      },
      boxShadow: {
        panel: '0 1px 2px rgba(15, 23, 42, 0.08)',
      },
    },
  },
  plugins: [forms],
};
