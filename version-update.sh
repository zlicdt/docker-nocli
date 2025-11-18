#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_FILE="$ROOT_DIR/version.txt"
PYPROJECT_FILE="$ROOT_DIR/api/backend/pyproject.toml"
VERSION="$(tr -d '\r\n ' < "$VERSION_FILE")"

sed -E -i.bak "0,/^(version\s*=\s*\")([^\"]+)(\".*)$/s//\1$VERSION\3/" "$PYPROJECT_FILE"
rm -f "${PYPROJECT_FILE}.bak"

echo "Updated $(realpath "$PYPROJECT_FILE") to version $VERSION"
