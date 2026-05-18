import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',  // ← явно указываем папку билда
    emptyOutDir: true, // ← очищать перед билдом
  },
})