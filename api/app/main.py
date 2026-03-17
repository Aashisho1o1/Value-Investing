from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import Analyzer
from app.services.cache import FileCache
from app.services.llm import DeepSeekClient
from app.services.sec_client import SECClient


settings = get_settings()
cache = FileCache(settings.cache_dir)
sec_client = SECClient(settings.sec_user_agent, cache)
llm_client = DeepSeekClient(settings)
analyzer = Analyzer(sec_client, llm_client, cache)

app = FastAPI(title="Value 10-K Analyzer", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return analyzer.analyze(request.ticker, request.force_refresh)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise HTTPException(status_code=502, detail=f"Analysis failed: {exc}") from exc
