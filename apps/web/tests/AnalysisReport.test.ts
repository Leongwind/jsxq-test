import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import AnalysisReport from '../src/components/AnalysisReport.vue'
import type { AnalysisResult } from '../src/types'

const result: AnalysisResult = {
  requestId: 'req-1', job: { id: 'java', title: '后端开发' },
  resume: { summary: 'Java 后端候选人', education: [], experience: [], projects: [], skills: [{ name: 'Java', evidence: 'Java 开发' }] },
  issues: [], matchedSkills: [{ name: 'Java', weight: 3, requirementEvidence: '熟悉 Java', resumeEvidence: 'Java 开发' }],
  missingSkills: [{ name: 'Redis', weight: 1, requirementEvidence: '了解 Redis', suggestion: '简历未体现 Redis 的证据。' }],
  score: 75, scoreBreakdown: { matchedWeight: 3, totalWeight: 4, formula: 'round(100 × matchedWeight / totalWeight)' }, warnings: [],
  meta: { mode: 'test', model: 'fixture', durationMs: 1200 },
}

describe('AnalysisReport', () => {
  it('renders evidence, reproducible score and a visible test warning', () => {
    const wrapper = mount(AnalysisReport, { props: { result } })
    expect(wrapper.text()).toContain('测试模式结果')
    expect(wrapper.text()).toContain('75')
    expect(wrapper.text()).toContain('Java 开发')
    expect(wrapper.text()).toContain('简历未体现 Redis')
    expect(wrapper.text()).toContain('3 / 4')
  })
})
