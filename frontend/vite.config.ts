import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
  root: './src',
  plugins: [react()],
    server: {
      port: 3000,
    },
    build: { manifest: true, outDir: 'dist', assetsDir: 'static' },
})
