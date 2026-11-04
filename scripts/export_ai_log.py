"""Export visible user/assistant messages only; never internal reasoning or tool secrets."""
import argparse
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("session", type=Path, help="Local Codex JSONL for this assessment only")
parser.add_argument("--output", type=Path, default=Path("docs/AI_CONVERSATION.md"))
args = parser.parse_args()
secrets = []
env = Path(".env")
if env.exists():
    for line in env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            if any(marker in key.upper() for marker in ("KEY", "TOKEN", "SECRET")):
                value = value.strip().strip('"').strip("'")
                if value:
                    secrets.append(value)


def redact(text):
    for secret in secrets:
        text = text.replace(secret, "[REDACTED]")
    return re.sub(r"\b(?:sk-|ghp_|gho_)[A-Za-z0-9_-]{12,}", "[REDACTED]", text)


sections = [
    "# 可见 AI 会话记录\n",
    "从本次 Codex 会话导出用户消息和助手可见回复。系统/开发者指令、环境快照、内部推理、工具原始输出不在此记录中。工具执行摘要与验证结果见 AI_LOG.md 和 DELIVERY.md。密钥已脱敏。时间戳为 UTC。\n",
]
count = 0
for line in args.session.read_text().splitlines():
    event = json.loads(line)
    payload = event.get("payload", {})
    if event.get("type") != "response_item" or payload.get("type") != "message":
        continue
    role = payload.get("role")
    if role not in ("user", "assistant") or payload.get("channel") in ("analysis", "summary"):
        continue
    content = payload.get("content", [])
    text = "\n".join(
        item.get("text", "") for item in content
        if item.get("type") in ("input_text", "output_text", "text")
    ).strip()
    if not text or text.startswith(("<external_codex_apps_open_page>", "# AGENTS.md instructions")):
        continue
    sections.append(f"## {event.get('timestamp', 'timestamp unavailable')} · {role}\n\n{redact(text)}\n")
    count += 1
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text("\n".join(sections))
print(f"Exported {count} visible messages; secrets redacted.")
