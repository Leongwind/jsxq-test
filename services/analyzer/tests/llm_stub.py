import json
import re

from fastapi import FastAPI, Request

app = FastAPI(title="Explicit CI LLM Stub")


def _between(value: str, tag: str) -> str:
    matched = re.search(rf"<{tag}>\n(.*?)\n</{tag}>", value, re.S)
    return matched.group(1) if matched else ""


SKILLS = [
    "Java",
    "Spring Boot",
    "Redis",
    "MySQL",
    "Docker",
    "Vue 3",
    "Vue",
    "TypeScript",
    "JavaScript",
]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": "test"}


@app.post("/chat/completions")
async def completions(request: Request) -> dict[str, object]:
    payload = await request.json()
    user_message = payload["messages"][-1]["content"]
    resume = _between(user_message, "resume")
    job = _between(user_message, "job")

    def evidence(source: str, name: str) -> str | None:
        phrase = r"[\s._-]*".join(re.escape(part) for part in re.split(r"[\s._-]+", name))
        for line in source.splitlines():
            for clause in re.split(r"(?<=[。；;])", line):
                if re.search(rf"(?<![a-z0-9]){phrase}(?![a-z0-9])", clause, re.I):
                    return clause.strip()
        return None

    skills = []
    requirements = []
    seen_resume: set[str] = set()
    seen_job: set[str] = set()
    for name in SKILLS:
        resume_line = evidence(resume, name)
        if resume_line and name.casefold() not in seen_resume:
            skills.append({"name": name, "evidence": resume_line})
            seen_resume.add(name.casefold())
        job_line = evidence(job, name)
        if job_line and name.casefold() not in seen_job:
            preferred = any(word in job_line for word in ("优先", "加分"))
            requirements.append(
                {
                    "name": name,
                    "priority": "preferred" if preferred else "required",
                    "evidence": job_line,
                }
            )
            seen_job.add(name.casefold())
    extraction = {
        "summary": "测试桩生成的确定性摘要",
        "education": [],
        "experience": [],
        "projects": [],
        "skills": skills,
        "requirements": requirements,
        "issues": [],
    }
    return {
        "id": "stub-completion",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(extraction, ensure_ascii=False),
                },
            }
        ],
    }
