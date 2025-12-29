import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import { fileURLToPath, URL } from "url";
import Components from "unplugin-vue-components/vite";
import { BootstrapVueNextResolver } from "bootstrap-vue-next";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [BootstrapVueNextResolver()],
    }),
  ],
  root: resolve("./src"),
  base: "/static/",
  build: {
    outDir: resolve("./dist"),
    assetsDir: "./src/assets",
    manifest: "manifest.json",
    emptyOutDir: true,
    rollupOptions: {
      // Overwrite default .html entry to main.ts in the static directory
      input: resolve("./src/main.ts"),
      output: {
        manualChunks(id) {
          if (id.includes("node_modules")) {
            if (id.includes("vue")) return "vue";
            return id
              .toString()
              .split("node_modules/")[1]
              .split("/")[0]
              .toString();
          }
        },
      },
    },
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      "@assets": fileURLToPath(new URL("./src/assets", import.meta.url)),
      "@components": fileURLToPath(
        new URL("./src/components", import.meta.url),
      ),
      "@pages": fileURLToPath(new URL("./src/pages", import.meta.url)),
      "@layouts": fileURLToPath(new URL("./src/layouts", import.meta.url)),
      "@node_modules": fileURLToPath(
        new URL("./node_modules", import.meta.url),
      ),
      "@types": fileURLToPath(new URL("./src/types", import.meta.url)),
      "@configurations": fileURLToPath(
        new URL("./src/configurations", import.meta.url),
      ),
    },
  },
  server: {
    origin: "http://localhost:5173",
    port: 5173,
    host: true,
    watch: {
      usePolling: true,
    },
  },
  css: {
    preprocessorOptions: {
      sass: {
        api: "modern",
        silenceDeprecations: ["import", "slash-div", "global-builtin"],
        quietDeps: true,
      },
      scss: {
        api: "modern",
        silenceDeprecations: ["import", "slash-div", "global-builtin"],
        quietDeps: true,
      },
    },
  },
});
