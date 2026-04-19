import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  use: {
    baseURL: 'https://aicraftspeopleguild.github.io',
    headless: true,
    viewport: { width: 1280, height: 720 },
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } }
  ],
  snapshotDir: './tests/snapshots',
  reporter: [['html', { open: 'never' }]],
});
