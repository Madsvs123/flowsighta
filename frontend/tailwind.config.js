/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "media",
  theme: {
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", "Segoe UI", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      colors: {
        ink: {
          950: "#07111a",
          900: "#0c1b27",
          800: "#132433",
          700: "#1c3346",
        },
        accent: {
          400: "#2dd4bf",
          500: "#14b8a6",
          600: "#0f766e",
        },
      },
      boxShadow: {
        panel: "0 18px 50px -24px rgba(7, 17, 26, 0.55)",
      },
    },
  },
  plugins: [],
};
