# Local development

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Python only

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
PYTHONPATH=packages:. uvicorn apps.api.main:app --reload
```

## Web only

```bash
cd apps/web
corepack enable
pnpm install
pnpm dev
```

## CLI

```bash
hermes doctor
hermes plan "A CRM for home service contractors"
hermes crew create "appointment scheduling crew" --write
```
