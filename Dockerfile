FROM python:3.12.9-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

COPY pyproject.toml* uv.lock* /app/

RUN uv venv && \
    uv sync --frozen --no-dev


FROM python:3.12.9-slim

LABEL org.opencontainers.image.source=https://github.com/fan9704/EScheduler
LABEL org.opencontainers.image.description="This is EScheduler Docker Image."
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

COPY --from=builder /app/.venv /app/.venv
COPY . /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV POSTGRES_USER=test
ENV POSTGRES_PASSWORD=123456
ENV POSTGRES_DB=drawing
ENV POSTGRES_PORT=5432
ENV POSTGRES_HOST=127.0.0.1
ENV POSTGRES_TEST_DB=test
ENV GENERATE_DB_SCHEMA=True
ENV TZ=Asia/Taipei

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
