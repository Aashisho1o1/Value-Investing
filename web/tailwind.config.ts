import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
    "../shared/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#14231b",
        moss: "#2e5b47",
        pine: "#1d3d31",
        sand: "#efe7d5",
        parchment: "#f8f3e7",
        ember: "#8f4c36",
      },
      boxShadow: {
        card: "0 18px 60px rgba(20, 35, 27, 0.08)",
      },
      backgroundImage: {
        mesh:
          "radial-gradient(circle at top left, rgba(159, 183, 143, 0.32), transparent 38%), radial-gradient(circle at top right, rgba(143, 186, 171, 0.26), transparent 32%), linear-gradient(135deg, rgba(239, 231, 213, 0.98), rgba(248, 243, 231, 0.98))",
      },
      fontFamily: {
        display: ['"Iowan Old Style"', '"Palatino Linotype"', "serif"],
        sans: ['"Avenir Next"', '"Segoe UI"', "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;

