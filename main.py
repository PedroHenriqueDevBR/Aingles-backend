from fastapi import FastAPI
from routers import core, articles, card
from services import sqlite_service


app = FastAPI()

@app.on_event("startup")
def on_startup() -> None:
    sqlite_service.create_db_and_tables()

app.include_router(core.router)
app.include_router(articles.router, prefix="/article")
app.include_router(card.router, prefix="/card")
