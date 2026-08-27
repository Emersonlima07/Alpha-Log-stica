import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: "#0B0F0C",
          900: "#10150F",
          800: "#171D15",
          700: "#232B20",
        },
        pine: {
          600: "#4CD137",
          500: "#6EE84A",
          100: "#E6FBDE",
        },
        rust: {
          600: "#B4432F",
          100: "#F7E7E3",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
