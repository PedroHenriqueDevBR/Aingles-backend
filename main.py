from typing import Union

from fastapi import FastAPI, HTTPException
from sqlmodel import select

from models.article_model import Article
from services import sqlite_service

app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    sqlite_service.create_db_and_tables()


@app.get("/")
def read_root() -> dict[str, Union[str, int]]:
    return {"message": "Hello, World!", "status": 200}


@app.post("/article/")
def create_article(article: Article, session: sqlite_service.SessionDep) -> Article:
    session.add(article)
    session.commit()
    session.refresh(article)
    return article


@app.put("/article/{article_id}")
def update_article(
    article_id: int, article_args: Article, session: sqlite_service.SessionDep
) -> Article:
    article = session.get(Article, article_id)

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article.title = article_args.title
    article.content = article_args.content
    session.commit()
    session.refresh(article)
    return article


@app.get("/article/")
def get_articles(session: sqlite_service.SessionDep) -> list[Article]:
    articles = session.exec(select(Article).offset(0).limit(100)).all()
    return articles


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
