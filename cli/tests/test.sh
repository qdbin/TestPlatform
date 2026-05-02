#!/bin/bash
set -e

# Install curl
apt-get update
apt-get install -y curl

# Install uv and all dependencies using pip
pip3 install --break-system-packages uv pytest pytest-json-ctrf typer rich httpx pyyaml appdirs


SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Run pytest with CTRF output using system python
pytest --ctrf /logs/verifier/ctrf.json $SCRIPT_DIR/test_outputs.py -rA

if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
