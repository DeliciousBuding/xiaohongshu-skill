FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.4 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PATH=/app/.venv/bin:$PATH

WORKDIR /app

COPY pyproject.toml uv.lock README.md LICENSE ./
RUN uv sync --frozen --no-dev --no-install-project

COPY scripts ./scripts
RUN uv sync --frozen --no-dev \
    && playwright install --with-deps chromium \
    && useradd --create-home --uid 10001 app \
    && mkdir -p /app/data /home/app/.xiaohongshu \
    && chown -R app:app /app /home/app/.xiaohongshu /ms-playwright

USER app
ENV HOME=/home/app

ENTRYPOINT ["python", "-m", "scripts"]
CMD ["check-login"]
