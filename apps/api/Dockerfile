FROM python:3.12-slim

WORKDIR /repo
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/repo/packages:/repo

RUN pip install --no-cache-dir --upgrade pip uv

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps/api ./apps/api
COPY crews ./crews

RUN uv pip install --system -e .

EXPOSE 8000
CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
