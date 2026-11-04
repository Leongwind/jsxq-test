import { expect, test } from '@playwright/test'

test('completes the full user journey through the public API', async ({ page }, testInfo) => {
  await page.goto('/')
  await expect(page.getByText('看清岗位要求')).toBeVisible()
  await page.getByRole('button', { name: /样例/ }).first().click()
  await page.locator('.n-base-selection').click()
  await page.locator('.n-base-select-option').first().click()
  const analysisResponse = page.waitForResponse(response =>
    response.url().endsWith('/api/analyses') && response.request().method() === 'POST',
  )
  await page.getByRole('button', { name: '开始匹配分析' }).click()
  const response = await analysisResponse
  expect(response.ok()).toBe(true)
  if (process.env.EXPECT_ANALYSIS_MODE) {
    const payload = await response.json() as { meta?: { mode?: string } }
    expect(payload.meta?.mode).toBe(process.env.EXPECT_ANALYSIS_MODE)
  }
  await expect(page.getByText('你的匹配证据图谱')).toBeVisible({ timeout: 70_000 })
  await expect(page.getByText('请求链与评分诊断')).toBeVisible()
  const viewport = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    viewportWidth: document.documentElement.clientWidth,
  }))
  expect(viewport.scrollWidth).toBeLessThanOrEqual(viewport.viewportWidth)
  await page.screenshot({ path: testInfo.outputPath('report.png'), fullPage: true })
})
