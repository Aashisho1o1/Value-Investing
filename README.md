# Value Investing: 10-K Value Memo

Prototype web app that turns the latest SEC 10-K for a public company into a cited, value-investing style research memo.

## Structure

- `web/`: Next.js 15 frontend
- `api/`: FastAPI backend
- `shared/`: shared TypeScript contract consumed by the frontend

## Local development

### Backend

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd web
npm install
npm run dev
```

## Required environment variables

### `api/.env`

```bash
SEC_USER_AGENT=Your Name your.email@example.com
DEEPSEEK_API_KEY=your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
CACHE_DIR=./cache
```

### `web/.env.local`

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

