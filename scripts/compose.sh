#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "${CAREERLENS_MIRROR:-}" ]]; then
  export NODE_IMAGE="${CAREERLENS_MIRROR}/node:24-bookworm-slim"
  export NGINX_IMAGE="${CAREERLENS_MIRROR}/nginx:1.28-alpine"
  export MAVEN_IMAGE="${CAREERLENS_MIRROR}/maven:3.9.11-eclipse-temurin-21"
  export JAVA_IMAGE="${CAREERLENS_MIRROR}/eclipse-temurin:21-jre-jammy"
  export PYTHON_IMAGE="${CAREERLENS_MIRROR}/python:3.12-slim"
fi
if docker compose version >/dev/null 2>&1; then
  exec docker compose "$@"
else
  exec docker-compose "$@"
fi
