#!/usr/bin/env bash
# Deploy or roll back using a specific immutable commit tag.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! "${1:-}" =~ ^[0-9a-f]{7,40}$ ]]; then
  echo "Usage: scripts/deploy.sh <commit-sha> [--local]"
  exit 2
fi
export IMAGE_TAG="$1"
if [[ "${2:-}" == "--local" ]]; then
  for service in web bff jobs analyzer; do
    docker image inspect "ghcr.io/leongwind/jsxq-test-${service}:${IMAGE_TAG}" >/dev/null
  done
fi
if [[ "${2:-}" != "--local" ]]; then
  scripts/compose.sh -f compose.yml pull
fi
scripts/compose.sh -f compose.yml up -d --no-build --wait
web_address="$(scripts/compose.sh -f compose.yml port web 80)"
python3 scripts/smoke.py --url "http://${web_address}"
echo "Running commit tag: $IMAGE_TAG"
