import Fastify, { type FastifyError } from 'fastify';
import { randomUUID } from 'node:crypto';

type Options = { javaUrl?: string; timeoutMs?: number; fetcher?: typeof fetch; logger?: boolean };
const errorCodes = new Set(['INVALID_INPUT','JOB_NOT_FOUND','UNANALYZABLE_JD','RATE_LIMITED','LLM_INVALID_RESPONSE','LLM_UPSTREAM_ERROR','UPSTREAM_ERROR','LLM_NOT_CONFIGURED','SERVICE_UNAVAILABLE','UPSTREAM_TIMEOUT']);

export function buildApp(options: Options = {}) {
  const app = Fastify({
    logger: options.logger ?? false,
    genReqId: () => randomUUID(),
    requestIdHeader: false,
    bodyLimit: 256 * 1024,
    ajv: { customOptions: { removeAdditional: false, coerceTypes: false } },
  });
  const javaUrl = (options.javaUrl ?? process.env.JAVA_URL ?? 'http://localhost:8081').replace(/\/$/, '');
  const fetcher = options.fetcher ?? fetch;
  const timeoutMs = options.timeoutMs ?? 55_000;

  app.addHook('onRequest', async (request, reply) => { reply.header('X-Request-Id', request.id); });
  app.setErrorHandler<FastifyError>((error, request, reply) => {
    const invalid = !!error.validation || error.statusCode === 400 || error.statusCode === 413 || error.statusCode === 415;
    reply.code(invalid ? 400 : 503).send({ code: invalid ? 'INVALID_INPUT' : 'SERVICE_UNAVAILABLE', message: invalid ? '请输入有效 JSON，并检查必填字段、字段长度和岗位选择。' : '服务暂时不可用，请稍后重试。', requestId: request.id });
  });
  app.get('/health', async () => ({ status: 'ok', service: 'bff', version: process.env.APP_VERSION ?? 'dev' }));

  async function forward(path: string, requestId: string, body?: unknown) {
    try {
      const response = await fetcher(`${javaUrl}${path}`, {
        method: body === undefined ? 'GET' : 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Request-Id': requestId },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: AbortSignal.timeout(timeoutMs),
      });
      const data = await response.json() as Record<string, unknown>;
      if (!response.ok) {
        const known = typeof data.code === 'string' && errorCodes.has(data.code);
        return { status: known && [400,404,422,429,502,503,504].includes(response.status) ? response.status : 502,
          data: { code: known ? data.code : 'UPSTREAM_ERROR', message: known && typeof data.message === 'string' ? data.message : '分析服务暂时不可用，请稍后重试。', requestId } };
      }
      return { status: response.status, data: body === undefined ? data : { ...data, requestId } };
    } catch (error) {
      const timeout = error instanceof Error && ['TimeoutError','AbortError'].includes(error.name);
      return { status: timeout ? 504 : 502, data: { code: timeout ? 'UPSTREAM_TIMEOUT' : 'UPSTREAM_ERROR', message: timeout ? '分析超时，请稍后重试或缩短文本。' : '无法连接分析服务，请稍后重试。', requestId } };
    }
  }
  app.get('/api/jobs', async (request, reply) => { const r = await forward('/internal/jobs', request.id); return reply.code(r.status).send(r.data); });
  app.post('/api/analyses', {
    schema: { body: {
      type: 'object', additionalProperties: false, required: ['resumeText'],
      properties: {
        resumeText: { type: 'string', minLength: 1, maxLength: 20000, pattern: '\\S' },
        jobId: { type: 'string', minLength: 1, maxLength: 100, pattern: '\\S' },
        jobText: { type: 'string', minLength: 1, maxLength: 12000, pattern: '\\S' },
      },
      oneOf: [{ required: ['jobId'], not: { required: ['jobText'] } }, { required: ['jobText'], not: { required: ['jobId'] } }],
    } },
  }, async (request, reply) => {
    const result = await forward('/internal/analyses', request.id, request.body);
    return reply.code(result.status).send(result.data);
  });
  return app;
}
