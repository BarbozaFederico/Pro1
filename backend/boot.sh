#!/usr/bin/env bash
set -e

if [ -f "venv/Scripts/activate" ]; then
    source "venv/Scripts/activate"
elif [ -f "venv/bin/activate" ]; then
    source "venv/bin/activate"
else
    echo "No se encontro el entorno virtual. Ejecute primero: bash install.sh"
    exit 1
fi

exec python app.py
