import { defineConfig } from 'vite'
import react from '@vitejs/react-swc'
import path from 'path'
import { fileURLToPath } from 'url'

// Recreate __dirname for ES Modules
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig({
  plugins: [react()],
  root: '.', 
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist', 
  },
})
