import type { AnalysisResult, ApiErrorPayload, Job } from './types'

export class ApiError extends Error {
  constructor(public code: string, message: string, public requestId?: string, public status?: number) { super(message) }
}

async function readError(response: Response): Promise<ApiError> {
  let body: Partial<ApiErrorPayload> = {}
  try { body = await response.json() as ApiErrorPayload } catch { /* upstream may not be JSON */ }
  return new ApiError(body.code ?? 'UPSTREAM_ERROR', body.message ?? '服务暂时不可用，请稍后重试。', body.requestId, response.status)
}

export async function fetchJobs(signal?: AbortSignal): Promise<Job[]> {
  const response = await fetch('/api/jobs', { signal })
  if (!response.ok) throw await readError(response)
  const body = await response.json() as { jobs: Job[] }
  return body.jobs
}

export async function analyzeResume(payload: { resumeText: string; jobId?: string; jobText?: string }): Promise<AnalysisResult> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort('browser-timeout'), 65_000)
  try {
    const response = await fetch('/api/analyses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
    if (!response.ok) throw await readError(response)
    return await response.json() as AnalysisResult
  } catch (error) {
    if (controller.signal.aborted) throw new ApiError('BROWSER_TIMEOUT', '分析超过 65 秒，请稍后重试。')
    throw error
  } finally { window.clearTimeout(timeout) }
}
