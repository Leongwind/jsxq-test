<script setup lang="ts">
import { computed, ref } from 'vue'
import { NAlert, NButton, NCard, NIcon as Icon, NInput, NRadioButton, NRadioGroup, NSelect, NSkeleton, NTag, NTooltip } from 'naive-ui'
import { ArrowRight, FileText, Wand } from '@vicons/tabler'
import type { Job, ResumeSample } from '../types'

const props = defineProps<{ jobs: Job[]; samples: ResumeSample[]; jobsLoading: boolean; loading: boolean }>()
const emit = defineEmits<{ submit: [payload: { resumeText: string; jobId?: string; jobText?: string }]; retryJobs: [] }>()

const resumeText = ref('')
const jobMode = ref<'preset' | 'custom'>('preset')
const jobId = ref('')
const jobText = ref('')
const touched = ref(false)
const selectedJob = computed(() => props.jobs.find(job => job.id === jobId.value))
const resumeError = computed(() => touched.value && !resumeText.value.trim() ? '请粘贴简历文本或载入脱敏样例。' : resumeText.value.length > 20_000 ? '简历不能超过 20,000 字。' : '')
const jobError = computed(() => {
  if (!touched.value) return ''
  if (jobMode.value === 'preset') return jobId.value ? '' : '请选择目标岗位。'
  if (!jobText.value.trim()) return '请粘贴岗位 JD。'
  return jobText.value.length > 12_000 ? '岗位 JD 不能超过 12,000 字。' : ''
})

function applySample(sampleId: string) {
  const sample = props.samples.find(item => item.id === sampleId)
  if (sample) resumeText.value = sample.text
}
function submit() {
  touched.value = true
  if (resumeError.value || jobError.value) return
  emit('submit', jobMode.value === 'preset'
    ? { resumeText: resumeText.value.trim(), jobId: jobId.value }
    : { resumeText: resumeText.value.trim(), jobText: jobText.value.trim() })
}
</script>

<template>
  <NCard class="input-card" :bordered="false">
    <div class="section-heading">
      <div><span class="step">01</span><h2>准备分析材料</h2></div>
      <NTag :bordered="false" size="small" class="privacy-tag">不保存简历</NTag>
    </div>

    <section class="form-section">
      <div class="field-label"><label for="resume">简历文本</label><span>{{ resumeText.length.toLocaleString() }} / 20,000</span></div>
      <div v-if="samples.length" class="sample-row" aria-label="脱敏简历样例">
        <span>快速载入</span>
        <NButton v-for="sample in samples" :key="sample.id" size="tiny" quaternary @click="applySample(sample.id)">
          <template #icon><Icon><FileText /></Icon></template>{{ sample.title }}
        </NButton>
      </div>
      <NInput id="resume" v-model:value="resumeText" type="textarea" :autosize="{ minRows: 10, maxRows: 18 }" placeholder="粘贴教育经历、项目经历、实习经历与技能信息…" :status="resumeError ? 'error' : undefined" />
      <p v-if="resumeError" class="field-error">{{ resumeError }}</p>
    </section>

    <section class="form-section">
      <div class="field-label"><span>目标岗位</span><span>选择一项</span></div>
      <NRadioGroup v-model:value="jobMode" size="small" class="mode-switch">
        <NRadioButton value="preset">预置岗位</NRadioButton><NRadioButton value="custom">自定义 JD</NRadioButton>
      </NRadioGroup>
      <template v-if="jobMode === 'preset'">
        <NSkeleton v-if="jobsLoading" height="42px" :sharp="false" />
        <NAlert v-else-if="!jobs.length" type="warning" :bordered="false">岗位加载失败。<NButton text type="primary" @click="$emit('retryJobs')">重新加载</NButton></NAlert>
        <NSelect v-else v-model:value="jobId" :options="jobs.map(job => ({ label: `${job.company} · ${job.title}`, value: job.id }))" placeholder="选择希望匹配的开发岗位" :status="jobError ? 'error' : undefined" />
        <div v-if="selectedJob" class="job-preview">
          <div><strong>{{ selectedJob.title }}</strong><span>{{ selectedJob.company }}</span></div>
          <p>{{ selectedJob.description }}</p>
          <a :href="selectedJob.sourceUrl" target="_blank" rel="noreferrer">查看招聘来源 · 采集于 {{ selectedJob.collectedAt }}</a>
        </div>
      </template>
      <template v-else>
        <NInput v-model:value="jobText" type="textarea" :autosize="{ minRows: 6, maxRows: 12 }" placeholder="粘贴岗位职责、任职要求与加分项…" :status="jobError ? 'error' : undefined" />
        <div class="field-label after-input"><span>请保留“必备”与“加分”措辞，便于确定权重</span><span>{{ jobText.length.toLocaleString() }} / 12,000</span></div>
      </template>
      <p v-if="jobError" class="field-error">{{ jobError }}</p>
    </section>

    <NTooltip :disabled="!loading"><template #trigger>
      <NButton class="analyze-button" type="primary" size="large" block :loading="loading" :disabled="loading" @click="submit">
        <template #icon><Icon><Wand /></Icon></template>{{ loading ? '正在沿完整链路分析…' : '开始匹配分析' }}<Icon v-if="!loading" class="button-arrow"><ArrowRight /></Icon>
      </NButton>
    </template>分析通常需要 20–50 秒，请勿重复提交。</NTooltip>
    <p class="submit-note">AI 用于结构化提取，分数由可复算的技能权重算法生成。</p>
  </NCard>
</template>
