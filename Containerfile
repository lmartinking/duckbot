FROM python:3.10-slim-bookworm as build

# Install poetry
ENV POETRY_HOME=/opt/poetry
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==1.8.2

COPY . /app

WORKDIR /app
RUN python3 -m venv .venv
RUN $POETRY_HOME/bin/poetry install
RUN $POETRY_HOME/bin/poetry run python -m spacy download en_core_web_md

FROM python:3.10-slim-bookworm as fortunes

# Install fortune and extras
RUN apt update -y && apt install -y fortune-mod fortunes-min fortunes fortunes-bofh-excuses fortune-anarchism

# Add Dubya fortunes!
WORKDIR /tmp
ADD https://ftp.heanet.ie/mirrors/gentoo.org/distfiles/7d/Dubya-20050118.tar.gz .
RUN tar xzvf Dubya-*.gz && mv ./dubya/dubya* /usr/share/games/fortunes

FROM python:3.10-slim-bookworm

COPY --from=fortunes /usr/games/fortune /usr/games/fortune
COPY --from=fortunes /usr/share/games/fortunes /usr/share/games/fortunes
COPY --from=fortunes /lib/x86_64-linux-gnu/librecode.so.0 /lib/x86_64-linux-gnu/librecode.so.0

COPY --from=build /app /app

CMD ["/app/.venv/bin/python", "-m", "duckbot.bot"]

LABEL org.opencontainers.image.source=https://github.com/lmartinking/duckbot
LABEL org.opencontainers.image.authors="Lucas Martin-King"
