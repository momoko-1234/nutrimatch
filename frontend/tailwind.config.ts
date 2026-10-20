import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#17202A",
        mist: "#F6F8F7",
        leaf: "#2D7D5F",
        coral: "#D96C4A",
        amberline: "#C99A2E"
      }
    }
  },
  plugins: []
};

export default config;
