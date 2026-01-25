FROM ghcr.io/astral-sh/uv:alpine
ENV UV_NO_DEV=1

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked

COPY ./purge ./purge

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "purge:app"]
