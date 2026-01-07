import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Dev server proxy - only for local development
  // In production, Vercel rewrites handle API routing (see vercel.json)
  // server: {
  //   proxy: {
  //     "/api": {
  //       target: "http://localhost:8000",
  //       changeOrigin: true,
  //       secure: false,
  //     },
  //   },
  // },
});
