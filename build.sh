#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
poetry run pyinstaller Atomic-Bayttle.spec
