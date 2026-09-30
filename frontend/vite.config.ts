import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // `npm run dev` talks to a backend on :8000 (see README), same origin as in Docker.
  server: {
    proxy: { '/api': { target: 'http://127.0.0.1:8000', ws: true, changeOrigin: false } },
  },
  test: {
    include: ['src/**/*.test.ts'],
    environment: 'node',
  },
});
