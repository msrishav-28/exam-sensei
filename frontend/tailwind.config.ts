import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: ["class"],
    content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
  	extend: {
  		colors: {
  			background: '#0a0a0a',
  			foreground: '#ffffff',
  			primary: {
  				DEFAULT: '#10B981',
  				foreground: '#ffffff'
  			},
  			secondary: {
  				DEFAULT: '#27272a',
  				foreground: '#a3a3a3'
  			},
  			muted: {
  				DEFAULT: '#27272a',
  				foreground: '#a3a3a3'
  			},
  			accent: {
  				DEFAULT: '#10B981',
  				foreground: '#ffffff'
  			},
  			card: {
  				DEFAULT: 'rgba(255, 255, 255, 0.03)',
  				foreground: '#ffffff'
  			},
  			popover: {
  				DEFAULT: '#0a0a0a',
  				foreground: '#ffffff'
  			},
  			border: 'rgba(255, 255, 255, 0.1)',
  			input: 'rgba(255, 255, 255, 0.1)',
  			ring: '#10B981'
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        display: ['var(--font-space-grotesk)', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'spotlight': 'radial-gradient(circle at center, var(--tw-gradient-stops))',
      }
  	}
  },
  plugins: [require("tailwindcss-animate"), require("@tailwindcss/typography")],
};
export default config;
