import { afterEach, describe, expect, it, vi } from 'vitest';
import { buildApp } from '../src/app.js';
const apps: ReturnType<typeof buildApp>[] = [];
const create = (options = {}) => { const app = buildApp(options); apps.push(app); return app; };
afterEach(async () => { await Promise.all(apps.splice(0).map(app => app.close())); });

describe('BFF validation and service boundary', () => {
  it.each([
    {}, {resumeText:' ',jobId:'java-campus'}, {resumeText:'a'.repeat(20001),jobId:'java-campus'},
    {resumeText:'Java',jobId:'java-campus',jobText:'Java'}, {resumeText:'Java'},
    {resumeText:'Java',jobText:'x'.repeat(12001)}, {resumeText:'Java',jobId:'x',extra:true},
    {resumeText:123,jobId:'x'}, {resumeText:'Java',jobId:null},
  ])('rejects malformed input without calling Java: %j', async payload => {
    const fetcher = vi.fn(); const app = create({fetcher});
    const r = await app.inject({method:'POST',url:'/api/analyses',payload});
    expect(r.statusCode).toBe(400); expect(r.json().code).toBe('INVALID_INPUT'); expect(fetcher).not.toHaveBeenCalled();
  });
  it.each([{resumeText:'Java project',jobId:'java-campus'},{resumeText:'Vue project',jobText:'Vue required'}])('forwards valid input and a server-generated request id', async payload => {
    const fetcher = vi.fn().mockResolvedValue(Response.json({score:75,requestId:'wrong'})); const app = create({fetcher});
    const r = await app.inject({method:'POST',url:'/api/analyses',payload,headers:{'x-request-id':'untrusted'}});
    expect(r.statusCode).toBe(200); expect(r.json().score).toBe(75);
    expect(r.json().requestId).toBe(r.headers['x-request-id']); expect(r.json().requestId).not.toBe('untrusted');
    expect(fetcher.mock.calls[0][1].headers['X-Request-Id']).toBe(r.json().requestId);
  });
  it('returns Java jobs',async()=>{const app=create({fetcher:vi.fn().mockResolvedValue(Response.json({jobs:[{id:'java-campus'}]}))});const r=await app.inject('/api/jobs');expect(r.json().jobs[0].id).toBe('java-campus');});
  it('preserves controlled downstream errors',async()=>{const app=create({fetcher:vi.fn().mockResolvedValue(Response.json({code:'JOB_NOT_FOUND',message:'岗位不存在'}, {status:404}))});const r=await app.inject({method:'POST',url:'/api/analyses',payload:{resumeText:'Java',jobId:'missing'}});expect(r.statusCode).toBe(404);expect(r.json().code).toBe('JOB_NOT_FOUND');});
  it('maps timeout without leaking details',async()=>{const app=create({fetcher:vi.fn().mockRejectedValue(new DOMException('secret','TimeoutError'))});const r=await app.inject('/api/jobs');expect(r.statusCode).toBe(504);expect(r.body).not.toContain('secret');});
  it('maps unknown upstream errors without exposing upstream data',async()=>{const app=create({fetcher:vi.fn().mockResolvedValue(Response.json({code:'SECRET',message:'sensitive'}, {status:500}))});const r=await app.inject('/api/jobs');expect(r.statusCode).toBe(502);expect(r.body).not.toContain('sensitive');});
  it('health does not call upstream',async()=>{const fetcher=vi.fn();const app=create({fetcher});expect((await app.inject('/health')).statusCode).toBe(200);expect(fetcher).not.toHaveBeenCalled();});
});
