import { expect, test } from '@playwright/test'

test('completes the full user journey through the public API', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('看清岗位要求')).toBeVisible()
  await page.getByRole('button', { name: /样例/ }).first().click()
  await page.locator('.n-base-selection').click()
  await page.locator('.n-base-select-option').first().click()
  await page.getByRole('button', { name: '开始匹配分析' }).click()
  await expect(page.getByText('你的匹配证据图谱')).toBeVisible({ timeout: 70_000 })
  await expect(page.getByText('请求链与评分诊断')).toBeVisible()
})
