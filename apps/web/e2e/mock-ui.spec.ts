import { expect, test } from '@playwright/test'

const job = { id: 'java-campus', title: '后端开发工程师', company: '沐瞳科技', description: 'Java、Spring Boot、MySQL、REST API 与 Git', sourceUrl: 'https://example.com/job', collectedAt: '2026-11-04' }
const result = {
  requestId: 'ui-test-1', job: { id: job.id, title: job.title },
  resume: { summary: '具备 Java 后端项目经验，能够完成接口开发与容器化交付。', education: [], experience: [], projects: [], skills: [{ name: 'Java', evidence: '使用 Java 开发接口' }, { name: 'Docker', evidence: '通过 Docker 部署' }] },
  issues: [{ type: 'impact', severity: 'warning', evidence: '负责后端接口开发', suggestion: '补充接口规模、性能或业务结果。' }],
  matchedSkills: [{ name: 'Java', weight: 3, requirementEvidence: '熟悉 Java', resumeEvidence: '使用 Java 开发接口' }],
  missingSkills: [{ name: 'Redis', weight: 1, requirementEvidence: '了解 Redis 优先', suggestion: '简历未体现 Redis 的证据；如有相关经历，请补充具体实践。' }],
  score: 75, scoreBreakdown: { matchedWeight: 3, totalWeight: 4, formula: 'round(100 × matchedWeight / totalWeight)' }, warnings: [], meta: { mode: 'test', model: 'ui-fixture', durationMs: 1200 },
}

test.beforeEach(async ({ page }) => {
  await page.route('**/api/jobs', route => route.fulfill({ json: { jobs: [job] } }))
  await page.route('**/api/analyses', route => route.fulfill({ json: result }))
})

test('keeps the key workflow readable and reports test mode', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: /Java 后端/ }).click()
  await page.locator('.n-base-selection').click()
  await page.locator('.n-base-select-option').click()
  await page.getByRole('button', { name: '开始匹配分析' }).click()
  await expect(page.getByText('你的匹配证据图谱')).toBeVisible()
  await expect(page.getByText('测试模式结果')).toBeVisible()
  await expect(page.getByText('3 / 4')).toBeVisible()
  await expect(page.locator('body')).not.toHaveCSS('overflow-x', 'scroll')
})
