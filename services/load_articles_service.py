import logging

from sqlmodel import select

from models.article_model import Article
from services.onesignal_service import send_notification
from services.supabase_service import SessionDep
from services.techcrunch_service import TechCrunchResponse, TechCrunchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoadArticlesService:

    def load_latest(self, session: SessionDep):
        service = TechCrunchService()
        responses: list[TechCrunchResponse] = service.latest_posts()

        new_articles = []
        for res in responses:
            try:
                existing_article = session.exec(
                    select(Article).where(Article.content_url == res.url)
                ).first()
                if existing_article:
                    logger.info(f"Article already exists: {res.url}")
                    continue

            except Exception as e:
                logger.error(f"Error checking existing article: {e}")
                continue

            session.add(
                Article(
                    title=res.title,
                    content_url=res.url,
                    content=res.content,
                )
            )
            new_articles.append(res.to_json())
            session.commit()

        if len(new_articles) > 0:
            logger.info(f"Loaded {len(new_articles)} new articles.")
            send_notification(
                title="News to read",
                message=f"{len(new_articles)} new articles have been loaded.",
                data=new_articles,
            )

        logger.info("Finished loading latest articles.")

    def load_article_content(self, article: Article, session: SessionDep):
        service = TechCrunchService()
        content: str = service.get_post_content(article.content_url)
        article.content = content
        session.add(article)
        session.commit()
        session.refresh(article)
