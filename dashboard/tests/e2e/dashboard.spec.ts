import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('http://localhost:4173/');
  await expect(page).toHaveTitle(/Enterprise AI Platform/);
});

test('sidebar navigation works', async ({ page }) => {
  await page.goto('http://localhost:4173/');

  await page.click('text=Playground');
  await expect(page.locator('h1').first()).toHaveText('Agent Playground');
});
