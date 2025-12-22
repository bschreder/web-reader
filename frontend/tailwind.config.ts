import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        sky: '#0ea5e9',
        mint: '#5eead4',
        sand: '#f5f5f4',
        graphite: '#1f2937',
      },
      fontFamily: {
        display: ['"Space Grotesk"', '"Segoe UI"', 'sans-serif'],
        body: ['"DM Sans"', '"Segoe UI"', 'sans-serif'],
      },
      boxShadow: {
        lift: '0 10px 30px rgba(15, 23, 42, 0.1)',
      },
    },
  },
  plugins: [],
};

export default config;
