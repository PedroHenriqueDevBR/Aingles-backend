import os
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from fastapi import FastAPI

from routers import articles, auth, card, core, chat
from services import sqlite_service

load_dotenv()

debug = os.getenv("DEBUG", "false").lower() == "true"
scheduler = AsyncIOScheduler(timezone="America/Fortaleza")
scheduler_hour = int(os.getenv("SCHEDULER_HOUR", "0"))
scheduler_minute = int(os.getenv("SCHEDULER_MINUTE", "0"))

app = FastAPI(
    title="Aingles API",
    description="API com sistema de autenticação JWT e banco de dados SQLite",
    version="1.0.0",
    docs_url=None if not debug else "/docs",
    redoc_url=None if not debug else "/redoc",
    openapi_url=None if not debug else "/openapi.json",
)


@app.on_event("shutdown")
async def stop_scheduler():
    logging.info("Stopping scheduler...")
    scheduler.shutdown(wait=False)


@app.on_event("startup")
def on_startup() -> None:
    logging.info("Starting database and tables creation...")
    sqlite_service.create_db_and_tables()

    logging.info("Starting scheduler...")
    scheduler.add_job(
        func=articles.load_articles,
        trigger=CronTrigger(hour=scheduler_hour, minute=scheduler_minute),
    )
    scheduler.start()


# Public routes
app.include_router(
    core.router,
    prefix="",
    tags=["App"],
)

# Authentication routes
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Resource routes
app.include_router(
    articles.router,
    prefix="/article",
    tags=["Articles"],
)
app.include_router(
    card.router,
    prefix="/card",
    tags=["Cards"],
)
app.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)
