<script setup lang="ts">
import { computed } from 'vue'
import { NAlert, NCollapse, NCollapseItem, NIcon as Icon, NProgress, NTag } from 'naive-ui'
import { AlertTriangle, ArrowUpRight, Check, CircleCheck, Clock, Code, Target, Wand } from '@vicons/tabler'
import type { AnalysisResult } from '../types'

const props = defineProps<{ result: AnalysisResult }>()
const scoreTone = computed(() => props.result.score >= 80 ? 'strong' : props.result.score >= 60 ? 'medium' : 'developing')
const scoreLabel = computed(() => props.result.score >= 80 ? '高度覆盖' : props.result.score >= 60 ? '部分覆盖' : '待补证据')
const coverage = computed(() => `${props.result.scoreBreakdown.matchedWeight} / ${props.result.scoreBreakdown.totalWeight}`)
const hasStructuredProfile = computed(() => Boolean(
  props.result.resume.education.length || props.result.resume.experience.length || props.result.resume.projects.length,
))
</script>

<template>
  <div class="analysis-report">
    <NAlert v-if="result.meta.mode === 'test'" class="test-banner" type="warning" :bordered="false" title="测试模式结果">
      本报告由测试桩生成，只用于验证请求链，不能视为真实模型分析。
    </NAlert>

    <div class="report-header">
      <div><span class="eyebrow">分析完成 · {{ result.job.title }}</span><h2>你的匹配证据图谱</h2></div>
      <NTag :bordered="false" round type="success"><template #icon><Icon><CircleCheck /></Icon></template>技能证据已校验</NTag>
    </div>

    <section class="score-card" :class="scoreTone">
      <div class="score-main">
        <div class="score-number"><strong>{{ result.score }}</strong><span>/ 100</span></div>
        <div><span class="score-label">{{ scoreLabel }}</span><p>可验证技能覆盖度</p></div>
      </div>
      <NProgress type="line" :percentage="result.score" :show-indicator="false" :height="8" color="#0c8d77" rail-color="rgba(12,141,119,.12)" />
      <div class="score-foot"><span>命中权重 <strong>{{ coverage }}</strong></span><span>必备项 × 3 · 加分项 × 1</span></div>
    </section>

    <section class="summary-card">
      <div class="section-title"><Icon><Wand /></Icon><h3>简历画像</h3></div>
      <p>{{ result.resume.summary }}</p>
      <div v-if="result.resume.skills.length" class="skill-cloud"><NTag v-for="skill in result.resume.skills" :key="skill.name" :bordered="false" size="small">{{ skill.name }}</NTag></div>
      <NCollapse v-if="hasStructuredProfile" class="profile-details">
        <NCollapseItem title="查看结构化经历" name="profile">
          <div class="profile-groups">
            <section v-if="result.resume.education.length"><h4>教育背景</h4><ul><li v-for="item in result.resume.education" :key="item">{{ item }}</li></ul></section>
            <section v-if="result.resume.experience.length"><h4>工作或实习经历</h4><ul><li v-for="item in result.resume.experience" :key="item">{{ item }}</li></ul></section>
            <section v-if="result.resume.projects.length"><h4>项目经历</h4><ul><li v-for="item in result.resume.projects" :key="item">{{ item }}</li></ul></section>
          </div>
        </NCollapseItem>
      </NCollapse>
    </section>

    <div class="result-columns">
      <section class="evidence-list matched-list">
        <div class="section-title"><Icon><Check /></Icon><h3>已命中 <span>{{ result.matchedSkills.length }}</span></h3></div>
        <div v-if="!result.matchedSkills.length" class="list-empty">暂未找到可验证的技能命中。</div>
        <article v-for="skill in result.matchedSkills" :key="skill.name">
          <div class="skill-head"><strong>{{ skill.name }}</strong><NTag size="tiny" :bordered="false">权重 {{ skill.weight }}</NTag></div>
          <p class="requirement"><Target />{{ skill.requirementEvidence }}</p><blockquote>“{{ skill.resumeEvidence }}”</blockquote>
        </article>
      </section>
      <section class="evidence-list missing-list">
        <div class="section-title"><Icon><ArrowUpRight /></Icon><h3>待补证据 <span>{{ result.missingSkills.length }}</span></h3></div>
        <div v-if="!result.missingSkills.length" class="list-empty">岗位要求均有对应证据。</div>
        <article v-for="skill in result.missingSkills" :key="skill.name">
          <div class="skill-head"><strong>{{ skill.name }}</strong><NTag size="tiny" :bordered="false">权重 {{ skill.weight }}</NTag></div>
          <p class="requirement"><Target />{{ skill.requirementEvidence }}</p><p class="suggestion">{{ skill.suggestion }}</p>
        </article>
      </section>
    </div>

    <section class="issue-section">
      <div class="section-title"><Icon><AlertTriangle /></Icon><h3>简历改进清单 <span>{{ result.issues.length }}</span></h3></div>
      <div v-if="!result.issues.length" class="list-empty">本次没有发现需要优先处理的结构化问题。</div>
      <article v-for="(issue, index) in result.issues" :key="`${issue.type}-${index}`" class="issue-item">
        <span class="issue-index">{{ String(index + 1).padStart(2, '0') }}</span><div><strong>{{ issue.suggestion }}</strong><p v-if="issue.evidence">原文：“{{ issue.evidence }}”</p></div><NTag size="tiny" :type="issue.severity === 'warning' ? 'warning' : 'info'" :bordered="false">{{ issue.type }}</NTag>
      </article>
    </section>

    <NAlert v-for="warning in result.warnings" :key="warning" type="warning" :bordered="false">{{ warning }}</NAlert>
    <NCollapse class="diagnostics">
      <NCollapseItem title="请求链与评分诊断" name="diagnostics">
        <dl><div><dt><Clock />耗时</dt><dd>{{ (result.meta.durationMs / 1000).toFixed(1) }} 秒</dd></div><div><dt><Code />模型</dt><dd>{{ result.meta.model }}</dd></div><div><dt>请求 ID</dt><dd>{{ result.requestId }}</dd></div><div><dt>评分公式</dt><dd>{{ result.scoreBreakdown.formula }}</dd></div></dl>
        <p class="chain">Vue 3 <i></i> Node BFF <i></i> Spring Boot <i></i> Python <i></i> {{ result.meta.mode === 'live' ? 'LLM' : 'LLM 测试桩' }}</p>
      </NCollapseItem>
    </NCollapse>
  </div>
</template>
