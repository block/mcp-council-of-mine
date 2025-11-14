#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=.
exec uv run fastmcp run src/main.py
