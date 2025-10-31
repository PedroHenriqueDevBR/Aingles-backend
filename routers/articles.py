from fastapi import APIRouter, BackgroundTasks, HTTPException, Response
from sqlmodel import select

from models.article_model import Article
from services import supabase_service
from services.load_articles_service import LoadArticlesService
from utils.dependencies import CurrentUser

router = APIRouter()


@router.post("/create")
def create_article(
    current_user: CurrentUser,
    article: Article,
    session: supabase_service.SessionDep,
) -> Article:
    article.author_id = current_user.id
    session.add(article)
    session.commit()
    session.refresh(article)
    return article


@router.put("/{article_id}/update")
def update_article(
    current_user: CurrentUser,
    article_id: int,
    article_args: Article,
    session: supabase_service.SessionDep,
) -> Article:
    article = session.get(Article, article_id)
    if not article or article.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Article not found")

    article.title = article_args.title
    article.content = article_args.content
    session.commit()
    session.refresh(article)
    return article


@router.get("/")
def get_articles(
    current_user: CurrentUser,
    session: supabase_service.SessionDep,
) -> list[Article]:
    articles = session.exec(
        select(Article)
        .where(Article.author_id == current_user.id)
        .offset(0)
        .limit(100)
    ).all()
    return articles


@router.delete("/{article_id}/delete")
def delete_article(
    current_user: CurrentUser, article_id: int, session: supabase_service.SessionDep
) -> None:
    article = session.get(Article, article_id)
    if not article or article.author_id != current_user.id:
        raise HTTPException(status_code=404, detail="Article not found")

    session.delete(article)
    session.commit()
    return Response(status_code=204)


@router.post("/load")
async def load_articles(
    background_tasks: BackgroundTasks,
    session: supabase_service.SessionDep,
):
    service = LoadArticlesService()
    background_tasks.add_task(service.load_latest, session=session)
    return Response(status_code=200)


@router.post("/{article_id}/load_content")
def load_article_content(
    article_id: int,
    session: supabase_service.SessionDep,
) -> Article:
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    service = LoadArticlesService()
    service.load_article_content(article, session=session)
    return article
