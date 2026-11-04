import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it } from 'vitest'
import { NSelect } from 'naive-ui'
import InputPanel from '../src/components/InputPanel.vue'

const job = { id: 'java', title: '后端开发', company: '示例公司', description: '熟悉 Java', sourceUrl: 'https://example.com', collectedAt: '2026-11-04' }

describe('InputPanel', () => {
  it('prevents an empty submission and explains both missing fields', async () => {
    const wrapper = mount(InputPanel, { props: { jobs: [job], samples: [], jobsLoading: false, loading: false } })
    await wrapper.find('.analyze-button').trigger('click')
    expect(wrapper.text()).toContain('请粘贴简历文本')
    expect(wrapper.text()).toContain('请选择目标岗位')
    expect(wrapper.emitted('submit')).toBeUndefined()
  })

  it('loads a sample and submits exactly one job selector', async () => {
    const wrapper = mount(InputPanel, { props: { jobs: [job], samples: [{ id: 'sample', title: '样例', text: '我使用 Java 开发接口', source: 'resume_01.pdf' }], jobsLoading: false, loading: false } })
    await wrapper.find('.sample-row button').trigger('click')
    await wrapper.find('.n-base-selection').trigger('click')
    const select = wrapper.findComponent(NSelect)
    ;(select.props()['onUpdate:value'] as (value: string) => void)('java')
    await nextTick()
    await wrapper.find('.analyze-button').trigger('click')
    expect(wrapper.emitted('submit')?.[0]).toEqual([{ resumeText: '我使用 Java 开发接口', jobId: 'java' }])
  })
})
