# CareerLens API v1 (frozen contract)

All JSON keys use camelCase. Browser calls same-origin /api only. BFF creates a UUID request ID; all internal hops forward X-Request-Id. Errors: {"code":"INVALID_INPUT","message":"中文可操作说明","requestId":"uuid"}. Never return provider bodies, secrets or stack traces.

## Jobs
GET /api/jobs -> Java GET /internal/jobs -> {jobs: Job[]}.
Job = {id, title, company, description, sourceUrl, collectedAt}; all strings. GET /internal/jobs/{id} returns Job or 404 JOB_NOT_FOUND.

## Analysis
POST /api/analyses -> Java POST /internal/analyses.
Input = {resumeText: string, jobId?: string, jobText?: string}. Exactly one of jobId/jobText, no unknown properties. Nonblank resume <= 20000 characters, nonblank custom JD <= 12000 characters, jobId <= 100 characters. JSON body <= 256 KiB.
Java resolves preset or creates custom job {id: "custom", title: "自定义岗位", description: jobText}, then POST Python /internal/analyze with {resumeText, job: {id,title,description}}.

Success HTTP 200:
```json
{
  "requestId": "uuid",
  "job": {"id":"java-campus", "title":"后端开发工程师"},
  "resume": {"summary":"摘要", "education":[], "experience":[], "projects":[], "skills":[{"name":"Java","evidence":"使用 Java 开发接口"}]},
  "issues":[{"type":"impact","severity":"warning","evidence":"负责开发接口","suggestion":"补充结果与可核验指标"}],
  "matchedSkills":[{"name":"Java","weight":3,"requirementEvidence":"熟悉 Java","resumeEvidence":"使用 Java 开发接口"}],
  "missingSkills":[{"name":"Redis","weight":1,"requirementEvidence":"了解 Redis 优先","suggestion":"简历未体现 Redis 的证据；如有相关经历，请补充具体实践。"}],
  "score":75,
  "scoreBreakdown":{"matchedWeight":3,"totalWeight":4,"formula":"round(100 × matchedWeight / totalWeight)"},
  "warnings":[],
  "meta":{"mode":"live","model":"configured-model","durationMs":1000}
}
```

## LLM extraction schema
One OpenAI-compatible POST /chat/completions, server-side only. Structured content:
```json
{"summary":"", "education":[], "experience":[], "projects":[], "skills":[{"name":"Java","evidence":"原文片段"}], "requirements":[{"name":"Java","priority":"required","evidence":"JD原文片段"}], "issues":[{"type":"structure","severity":"warning","evidence":"原文片段或缺失问题时空字符串","suggestion":"建议"}]}
```
Required arrays, string elements for education/experience/projects. priority = required|preferred; severity = info|warning. All extracted fields are validated. Skill evidence must be grounded in resume; requirement evidence in JD. Dedupe canonical skills, required weight 3 overrides preferred weight 1. Preserve meaningful versions (Vue 2 != Vue 3). Unsubstantiated skills cannot count. No requirements -> 422 UNANALYZABLE_JD, never fabricated score. Missing skills mean missing resume evidence, not inability. Do not use the LLM to produce final score.

## Errors and timeouts
400 INVALID_INPUT; 404 JOB_NOT_FOUND; 422 UNANALYZABLE_JD; 429 RATE_LIMITED; 502 LLM_INVALID_RESPONSE / LLM_UPSTREAM_ERROR / UPSTREAM_ERROR; 503 LLM_NOT_CONFIGURED / SERVICE_UNAVAILABLE; 504 UPSTREAM_TIMEOUT.
LLM timeout 40s; Python total 45s; Java outbound 50s; BFF outbound 55s; browser 65s; nginx 70s. No retry or silent fallback. Health checks never call LLM. Each service exposes /health (Java /actuator/health). No resume persistence or request-body logging. meta.mode=test only in explicit test configuration, UI visibly labels it.
