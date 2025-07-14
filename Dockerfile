FROM python:3.13-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv venv
RUN uv sync --frozen --no-cache
RUN uv build

# Run the application.
ENV MCP_ENVIRONMENT=PRODUCTION
ENV PORT=8000
EXPOSE 8000
ENTRYPOINT ["/app/.venv/bin/gunicorn", "biocontext_kb.app:app", "-c", "/app/config/gunicorn.py"]
