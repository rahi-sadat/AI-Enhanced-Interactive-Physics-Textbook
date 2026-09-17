import { defineConfig } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  resolve: {
    alias: {
      '@engine': path.resolve(__dirname, '../../engine'),
      '@shared': path.resolve(__dirname, '../../shared'),
      '@ai': path.resolve(__dirname, '../../ai'),
      '@features': path.resolve(__dirname, './src/features'),
      'matter-js': path.resolve(__dirname, 'node_modules/matter-js/build/matter.js'),
      'poly-decomp': path.resolve(__dirname, 'node_modules/poly-decomp/src/index.js'),
    },
  },
  server: {
    port: 5173,
    host: true,
    fs: {
      allow: ['..', '../..'],
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
