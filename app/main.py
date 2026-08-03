import asyncio
import html
import os
import secrets
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .collector import collect_all
from .db import init_db, list_jobs, set_status

security = HTTPBasic()
scheduler = AsyncIOScheduler()


def require_auth(credentials: HTTPBasicCredentials = Depends(security)):
    user_ok = secrets.compare_digest(credentials.username, os.getenv("DASHBOARD_USER", "admin"))
    pass_ok = secrets.compare_digest(credentials.password, os.getenv("DASHBOARD_PASSWORD", ""))
    if not (user_ok and pass_ok and os.getenv("DASHBOARD_PASSWORD")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Basic"})


@asynccontextmanager
async def lifespan(app):
    init_db()
    minutes = max(15, int(os.getenv("SCAN_INTERVAL_MINUTES", "60")))
    scheduler.add_job(collect_all, "interval", minutes=minutes, id="collect", max_instances=1, coalesce=True)
    scheduler.start()
    asyncio.create_task(collect_all())
    yield
    scheduler.shutdown()


app = FastAPI(title="Job Review Queue", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
def dashboard():
    rows = []
    for job in list_jobs():
        safe_source = html.escape(job["source"])
        safe_title = html.escape(job["title"])
        safe_url = html.escape(job["url"], quote=True)
        safe_status = html.escape(job["status"])
        actions = " ".join(
            f'<button name="status" value="{s}">{s.title()}</button>'
            for s in ("approved", "rejected", "applied")
        )
        rows.append(f"<tr><td>{safe_source}</td><td><a href=\"{safe_url}\" target=\"_blank\" rel=\"noopener noreferrer\">{safe_title}</a></td><td>{safe_status}</td><td><form method=post action=/jobs/{job['id']}/status>{actions}</form></td></tr>")
    return """<!doctype html><meta charset=utf-8><title>Job Review Queue</title>
    <style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 20px}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}button{margin:2px;padding:6px 10px}</style>
    <h1>Job Review Queue</h1><p>Applications are never submitted automatically.</p>
    <table><thead><tr><th>Source</th><th>Job</th><th>Status</th><th>Review</th></tr></thead><tbody>""" + "".join(rows) + "</tbody></table>"


@app.post("/jobs/{job_id}/status", dependencies=[Depends(require_auth)])
def update_status(job_id: int, status: str = Form(...)):
    set_status(job_id, status)
    return RedirectResponse("/", status_code=303)
