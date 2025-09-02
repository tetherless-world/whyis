import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue2';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./js/whyis_vue/tests/setup.js'],
    include: ['js/whyis_vue/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        'js/whyis_vue/tests/',
        '**/*.config.js'
      ]
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './js/whyis_vue'),
      'vue': 'vue/dist/vue.esm.js'
    }
  }
});