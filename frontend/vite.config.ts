import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import {resolve} from "path";
import {fileURLToPath, URL} from 'node:url'
import Components from 'unplugin-vue-components/vite'
import {BootstrapVueNextResolver} from 'bootstrap-vue-next'
import vitePluginRequire from "vite-plugin-require";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        Components({
            resolvers: [BootstrapVueNextResolver()],
        }),
        vitePluginRequire.default(),
    ],
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
            '@': fileURLToPath(new URL('./src', import.meta.url)),
            '@assets': fileURLToPath(new URL('./src/assets', import.meta.url)),
            '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
            '@pages': fileURLToPath(new URL('./src/pages', import.meta.url)),
            '@layouts': fileURLToPath(new URL('./src/layouts', import.meta.url)),
            '@node_modules': fileURLToPath(new URL('./node_modules', import.meta.url)),
            '@types': fileURLToPath(new URL('./src/types', import.meta.url)),
        }
    },
    server: {
        origin: "http://localhost:5173",
    }
})
