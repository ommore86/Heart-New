import { defineConfig } from 'vite'
import react from '@vitejs/react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  root: '.', // Explicitly tells Vite to use the frontend folder as root
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist', // Ensures the output goes exactly where Vercel expects it
  },
})
