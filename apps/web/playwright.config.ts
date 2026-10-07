import { defineConfig, devices } from '@playwright/test';
import path from 'node:path';

const root = path.resolve(__dirname, '../..');
const pythonPath = process.env.PYTHON_EXECUTABLE || (process.platform === 'win32' ? path.join(root, '.venv', 'Scripts', 'python.exe') : 'python');
const python = `"${pythonPath}"`;
export default defineConfig({
  testDir: './e2e',
  timeout: 60000,
  expect: { timeout: 10000 },
  fullyParallel: false,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:3000',
    ...devices['Desktop Chrome'],
    channel: process.env.PLAYWRIGHT_CHANNEL || undefined,
    launchOptions: { args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream'] },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: [
    { command: `${python} -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000`,
      cwd: root, url: 'http://127.0.0.1:8000/health', reuseExistingServer: !process.env.CI,
      env: { DATABASE_URL: `sqlite+aiosqlite:///${path.join(root, '.local/e2e.db').replaceAll('\\', '/')}`, ENVIRONMENT: 'test', DEMO_MODE: 'true' } },
    { command: 'npm start -- --hostname 127.0.0.1', url: 'http://127.0.0.1:3000', reuseExistingServer: !process.env.CI },
  ],
});

