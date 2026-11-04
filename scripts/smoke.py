"""No secrets or resume content are logged. --analyze adds one complete request."""
import argparse
import json
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://localhost:8080")
parser.add_argument("--analyze", action="store_true")
args = parser.parse_args()


def call(path, payload=None):
    request = urllib.request.Request(
        args.url + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=65) as response:
            body = response.read()
            return json.loads(body) if "json" in response.headers.get("content-type", "") else body
    except urllib.error.HTTPError as error:
        data = json.loads(error.read())
        raise SystemExit(f"HTTP {error.code}: {data.get('code')} requestId={data.get('requestId')}")


call("/health")
jobs = call("/api/jobs")["jobs"]
assert len(jobs) == 2 and all(job["sourceUrl"] for job in jobs)
print("PASS web health + BFF -> Java jobs")
if args.analyze:
    result = call(
        "/api/analyses",
        {"resumeText": "项目经历：使用 Java 和 SpringBoot 开发订单接口，使用 MySQL 保存订单。",
         "jobText": "必备技能：Java、Spring Boot、MySQL；加分项：Redis。"},
    )
    assert 0 <= result["score"] <= 100
    assert result["scoreBreakdown"]["totalWeight"] > 0
    assert result["requestId"] and result["meta"]["mode"] in ("live", "test")
    print("PASS full chain", json.dumps({
        "score": result["score"], "mode": result["meta"]["mode"],
        "requestId": result["requestId"], "model": result["meta"]["model"],
        "matched": len(result["matchedSkills"]), "missing": len(result["missingSkills"]),
    }, ensure_ascii=False))
