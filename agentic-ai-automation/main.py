"""FastAPI entrypoint — webhooks, manual triggers, metrics, and a live dashboard."""
import hashlib
import hmac
import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse

from agents import Orchestrator
from config import settings
from config.logging import configure_logging
from dashboard import render_dashboard
from models import WebhookEvent

configure_logging(settings.log_level, settings.json_logs)
logger = logging.getLogger(__name__)

orchestrator = Orchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await orchestrator.startup()
    yield
    orchestrator.shutdown()


app = FastAPI(
    title="Agentic AI Automation",
    description="Autonomous workflow automation with GitHub triage and reminders.",
    version="2.0.0",
    lifespan=lifespan,
)


def _verify_signature(payload: bytes, sig_header: str) -> None:
    if not settings.github_webhook_secret:
        return
    expected = "sha256=" + hmac.new(
        settings.github_webhook_secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, sig_header or ""):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature")


@app.post("/webhook/github", summary="Receive GitHub webhook events")
async def github_webhook(
    request: Request,
    background: BackgroundTasks,
    x_github_event: str = Header(...),
    x_github_delivery: str = Header(...),
    x_hub_signature_256: str = Header(""),
):
    payload_bytes = await request.body()
    _verify_signature(payload_bytes, x_hub_signature_256)
    payload = await request.json()

    event = WebhookEvent(
        event_type=x_github_event,
        action=payload.get("action"),
        delivery_id=x_github_delivery,
        issue=payload.get("issue"),
        pull_request=payload.get("pull_request"),
        repository_full_name=(payload.get("repository") or {}).get("full_name"),
    )
    # Acknowledge immediately; process in the background (GitHub expects <10s).
    background.add_task(orchestrator.handle_webhook, event)
    return {"status": "accepted", "delivery_id": x_github_delivery}


@app.post("/trigger/triage", summary="Manually run full issue triage")
async def trigger_triage():
    return {"status": "ok", "result": await orchestrator.run_full_triage()}


@app.post("/trigger/reminders", summary="Manually run PR reminder check")
async def trigger_reminders():
    return {"status": "ok", "result": await orchestrator.run_reminders()}


@app.get("/health", summary="Liveness probe")
async def health():
    return {"status": "healthy"}


@app.get("/metrics", summary="Automation metrics (JSON)")
async def metrics():
    return JSONResponse(await orchestrator.store.stats())


@app.get("/", response_class=HTMLResponse, summary="Live dashboard")
async def dashboard():
    stats = await orchestrator.store.stats()
    runs = await orchestrator.store.recent_runs(limit=25)
    return render_dashboard(stats, runs, settings.github_repo)
