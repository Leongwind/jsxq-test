export interface ResumeSample { id: string; title: string; text: string; source: string }
export interface Job { id: string; title: string; company: string; description: string; sourceUrl: string; collectedAt: string }
export interface SkillEvidence { name: string; evidence: string }
export interface ResumeProfile { summary: string; education: string[]; experience: string[]; projects: string[]; skills: SkillEvidence[] }
export interface Issue { type: string; severity: 'info' | 'warning'; evidence: string; suggestion: string }
export interface MatchedSkill { name: string; weight: number; requirementEvidence: string; resumeEvidence: string }
export interface MissingSkill { name: string; weight: number; requirementEvidence: string; suggestion: string }
export interface AnalysisResult {
  requestId: string
  job: Pick<Job, 'id' | 'title'>
  resume: ResumeProfile
  issues: Issue[]
  matchedSkills: MatchedSkill[]
  missingSkills: MissingSkill[]
  score: number
  scoreBreakdown: { matchedWeight: number; totalWeight: number; formula: string }
  warnings: string[]
  meta: { mode: 'live' | 'test'; model: string; durationMs: number }
}
export interface ApiErrorPayload { code: string; message: string; requestId?: string }
