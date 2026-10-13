import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  server: {
    port: 3000,

    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
        timeout: 10000,
        proxyTimeout: 10000,
      },

      '/ws': {
        target: 'http://localhost:8000',
        ws: true,
        changeOrigin: true,
        timeout: 10000,
        proxyTimeout: 10000,
      },
    },
  },

  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});