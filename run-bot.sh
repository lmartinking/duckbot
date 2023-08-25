#!/bin/bash

if [[ ! -d .venv ]] ; then
  # Install dependencies on first run
  poetry config --local virtualenvs.in-project true
  poetry install
fi

source .venv/bin/activate
source .env

# This appears to be necessary on Raspberry Pi, as certain Python libraries
# use atomic instructions via libatomic (at least on ARM).
if [[ -f /usr/lib/arm-linux-gnueabihf/libatomic.so.1 ]] ; then
  export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1
fi

[[ ! -z "$CAPYCOIN_HOST" ]] && python -m duckbot.capycoin  # Setup tables

python -m duckbot.bot
