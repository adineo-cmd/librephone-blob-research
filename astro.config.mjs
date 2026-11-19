import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  site: 'https://adineo-cmd.github.io',
  base: '/open-device',
  build: { format: 'file' },
});
