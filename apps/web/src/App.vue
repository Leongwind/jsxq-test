<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NButton, NConfigProvider, NIcon as Icon, NMessageProvider, useMessage, zhCN, dateZhCN, type GlobalThemeOverrides } from 'naive-ui'
import { AlertCircle, Refresh } from '@vicons/tabler'
import BrandMark from './components/BrandMark.vue'
import InputPanel from './components/InputPanel.vue'
import EmptyReport from './components/EmptyReport.vue'
import LoadingReport from './components/LoadingReport.vue'
import AnalysisReport from './components/AnalysisReport.vue'
import { analyzeResume, ApiError, fetchJobs } from './api'
import { getResumeSamples } from './samples'
import type { AnalysisResult, Job } from './types'

const themeOverrides: GlobalThemeOverrides = {
  common: { primaryColor: '#0c8d77', primaryColorHover: '#087562', primaryColorPressed: '#075e50', primaryColorSuppl: '#0c8d77', borderRadius: '10px', fontFamily: '"Avenir Next", "PingFang SC", "Microsoft YaHei", sans-serif' },
  Button: { heightLarge: '48px', borderRadiusLarge: '12px', fontWeight: '650' },
  Input: { borderRadius: '10px', boxShadowFocus: '0 0 0 3px rgba(12, 141, 119, .10)' },
  Card: { borderRadius: '18px' },
}

const jobs = ref<Job[]>([]), jobsLoading = ref(false), loading = ref(false)
const result = ref<AnalysisResult | null>(null), error = ref<ApiError | null>(null)
const lastPayload = ref<{ resumeText: string; jobId?: string; jobText?: string } | null>(null)
const samples = getResumeSamples()

async function loadJobs() {
  jobsLoading.value = true
  try { jobs.value = await fetchJobs() } catch { jobs.value = [] } finally { jobsLoading.value = false }
}
async function submit(payload: { resumeText: string; jobId?: string; jobText?: string }) {
  lastPayload.value = payload; loading.value = true; error.value = null; result.value = null
  try { result.value = await analyzeResume(payload) }
  catch (caught) { error.value = caught instanceof ApiError ? caught : new ApiError('NETWORK_ERROR', '无法连接分析服务，请检查网络后重试。') }
  finally { loading.value = false }
}
function retry() { if (lastPayload.value) void submit(lastPayload.value) }
onMounted(loadJobs)
</script>

<template>
  <NConfigProvider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <NMessageProvider>
      <div class="app-shell">
        <header class="site-header"><a class="brand" href="#" aria-label="CareerLens 首页"><BrandMark /><span>Career<strong>Lens</strong></span></a><div class="header-meta"><span class="live-dot"></span><span>Evidence-based matching</span><em>v1.0</em></div></header>
        <main>
          <div class="intro"><span class="kicker">CAREER INTELLIGENCE / 求职分析</span><h1>看清岗位要求，<br><em>找到下一步。</em></h1><p>把简历与真实岗位放在同一张证据图谱上。每个命中有出处，每个缺口有行动建议。</p></div>
          <div class="workspace-grid">
            <InputPanel :jobs="jobs" :samples="samples" :jobs-loading="jobsLoading" :loading="loading" @submit="submit" @retry-jobs="loadJobs" />
            <section class="report-pane" aria-live="polite" :aria-busy="loading">
              <LoadingReport v-if="loading" />
              <div v-else-if="error" class="error-report"><Icon size="36"><AlertCircle /></Icon><span class="eyebrow">分析未完成 · {{ error.code }}</span><h2>{{ error.message }}</h2><p v-if="error.requestId">请求 ID：{{ error.requestId }}</p><NButton type="primary" @click="retry"><template #icon><Icon><Refresh /></Icon></template>保留输入并重试</NButton></div>
              <AnalysisReport v-else-if="result" :result="result" />
              <EmptyReport v-else />
            </section>
          </div>
        </main>
        <footer><span>CAREERLENS / 2026</span><p>匹配分数表示简历中可验证的技能覆盖度，不代表录用概率。</p></footer>
      </div>
    </NMessageProvider>
  </NConfigProvider>
</template>
