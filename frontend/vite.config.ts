import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from "path";
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  root: resolve("./src"),
  base: "/static/",
  build: {
    outDir: resolve("./dist"),
    assetsDir: "./src/assets",
    manifest: true,
    emptyOutDir: true,
    rollupOptions: {
      // Overwrite default .html entry to main.ts in the static directory
      input: resolve("./src/main.ts"),
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    origin: "http://localhost:5173",
  }
})
