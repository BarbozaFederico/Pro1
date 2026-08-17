#!/usr/bin/env bash
set -e

PYTHON_CMD="${PYTHON_CMD:-python}"
"$PYTHON_CMD" -m venv venv

if [ -f "venv/Scripts/activate" ]; then
    source "venv/Scripts/activate"
else
    source "venv/bin/activate"
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
