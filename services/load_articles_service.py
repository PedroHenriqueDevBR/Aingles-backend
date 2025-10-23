from models.article_model import Article
from services.sqlite_service import SessionDep
from services.techcrunch_service import TechCrunchResponse, TechCrunchService


class LoadArticlesService:

    def load_latest(self, session: SessionDep):
        service = TechCrunchService()
        responses: list[TechCrunchResponse] = service.latest_posts()

        for res in responses:
            session.add(
                Article(
                    title=res.title,
                    content_url=res.url,
                    content=res.content,
                )
            )
            session.commit()

    def load_article_content(self, article: Article, session: SessionDep):
        service = TechCrunchService()
        content: str = service.get_post_content(article.content_url)
        article.content = content
        session.add(article)
        session.commit()
        session.refresh(article)