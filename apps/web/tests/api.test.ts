import { afterEach, describe, expect, it, vi } from 'vitest'
import { analyzeResume, ApiError, fetchJobs } from '../src/api'

afterEach(() => { vi.restoreAllMocks(); vi.useRealTimers() })

describe('API client', () => {
  it('loads the jobs envelope', async () => {
    const jobs = [{ id: 'java', title: 'Java', company: 'A', description: 'D', sourceUrl: 'https://example.com', collectedAt: '2026-11-04' }]
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ jobs }), { status: 200 })))
    await expect(fetchJobs()).resolves.toEqual(jobs)
  })

  it('preserves the structured error and request id', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ code: 'UNANALYZABLE_JD', message: '无法分析岗位', requestId: 'req-1' }), { status: 422 })))
    await expect(analyzeResume({ resumeText: 'Java', jobText: '你好' })).rejects.toMatchObject({ code: 'UNANALYZABLE_JD', requestId: 'req-1' })
  })

  it('maps the 65 second browser deadline to an actionable error', async () => {
    vi.useFakeTimers()
    vi.stubGlobal('fetch', vi.fn((_url, init: RequestInit) => new Promise((_resolve, reject) => {
      init.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))
    })))
    const pending = analyzeResume({ resumeText: 'Java', jobId: 'java' })
    const rejection = expect(pending).rejects.toMatchObject({ code: 'BROWSER_TIMEOUT' })
    await vi.advanceTimersByTimeAsync(65_000)
    await rejection
  })
})
