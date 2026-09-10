/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F5F6F3",
        ink: "#14201D",
        teal: {
          DEFAULT: "#1F5C52",
          dark: "#163F38",
          soft: "#E4EEEC",
        },
        amber: {
          DEFAULT: "#D98A34",
          soft: "#FBEEDD",
        },
        sage: {
          DEFAULT: "#6B9080",
          soft: "#E9F1EC",
        },
        clay: {
          DEFAULT: "#B5533C",
          soft: "#F6E7E2",
        },
        line: "#DEDDD5",
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        sans: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "6px",
      },
    },
  },
  plugins: [],
}
