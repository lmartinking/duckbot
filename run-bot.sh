#!/bin/bash

if [[ ! -d .venv ]] ; then
  # Install dependencies on first run
  poetry config --local virtualenvs.in-project true
  poetry install
fi

source .venv/bin/activate
source .env

python -m duckbot.bot
