import type { ResumeSample } from './types'

const modules = import.meta.glob('./data/resumes.json', { eager: true, import: 'default' })

export function getResumeSamples(): ResumeSample[] {
  const raw = modules['./data/resumes.json']
  if (!Array.isArray(raw)) return []
  return raw.filter((item): item is ResumeSample => Boolean(item && typeof item === 'object' && 'id' in item && 'title' in item && 'text' in item && 'source' in item))
}
