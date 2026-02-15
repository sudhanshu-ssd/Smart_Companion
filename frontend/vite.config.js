import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc' // Make sure "plugin-" is here!
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})