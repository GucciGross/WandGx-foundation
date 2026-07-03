FROM python:3.12-slim

WORKDIR /repo
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/repo/packages:/repo

RUN pip install --no-cache-dir --upgrade pip uv

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps/worker ./apps/worker
COPY crews ./crews

RUN uv pip install --system -e .

CMD ["python", "-m", "apps.worker.worker"]
