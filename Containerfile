FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY . /app

RUN uv sync --locked

FROM docker.io/library/python:3.12-slim-bookworm as fortunes

# Install fortune and extras
RUN apt update -y && apt install -y fortune-mod fortunes-min fortunes fortunes-bofh-excuses fortune-anarchism

# Add Dubya fortunes!
WORKDIR /tmp
ADD http://mirror.linux.ro/gentoo/distfiles/Dubya-20050118.tar.gz .
RUN tar xzvf Dubya-*.gz && mv ./dubya/dubya* /usr/share/games/fortunes

FROM docker.io/library/python:3.12-slim-bookworm

COPY --from=fortunes /usr/games/fortune /usr/games/fortune
COPY --from=fortunes /usr/share/games/fortunes /usr/share/games/fortunes
COPY --from=fortunes /lib/x86_64-linux-gnu/librecode.so.0 /lib/x86_64-linux-gnu/librecode.so.0

RUN groupadd --system --gid 999 nonroot && useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=build --chown=nonroot:nonroot /app /app

USER nonroot

WORKDIR /app

CMD ["/app/.venv/bin/python", "-m", "duckbot.bot"]

LABEL org.opencontainers.image.source=https://github.com/lmartinking/duckbot
LABEL org.opencontainers.image.authors="Lucas Martin-King"
