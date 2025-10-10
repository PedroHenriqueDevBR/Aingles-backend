from fastapi import APIRouter, HTTPException
from sqlmodel import select

from models.article_model import Article
from services import sqlite_service

router = APIRouter()


@router.post("/create")
def create_article(article: Article, session: sqlite_service.SessionDep) -> Article:
    session.add(article)
    session.commit()
    session.refresh(article)
    return article


@router.put("/{article_id}/update")
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


@router.get("/")
def get_articles(session: sqlite_service.SessionDep) -> list[Article]:
    articles = session.exec(select(Article).offset(0).limit(100)).all()
    return articles


@router.delete('/{article_id}/delete')
def delete_article(article_id: int, session: sqlite_service.SessionDep) -> None:
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    session.delete(article)
    session.commit()
