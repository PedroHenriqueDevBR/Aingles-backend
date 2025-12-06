import requests


class TabNewsResponse:
    
    def __init__(
        self,
        article_id: str,
        slug: str,
        title: str,
        status: str,
        published_at: str,
        tabcoins: str,
        owner_username: str,
        article_type: str,
    ):
        self.id = article_id
        self.slug = slug
        self.title = title
        self.status = status
        self.published_at = published_at
        self.tabcoins = tabcoins
        self.owner_username = owner_username
        self.article_type = article_type

    @staticmethod
    def from_dict(obj: dict) -> "TabNewsResponse":
        _id = str(obj.get("id"))
        _slug = str(obj.get("slug"))
        _title = str(obj.get("title"))
        _status = str(obj.get("status"))
        _published_at = str(obj.get("published_at"))
        _tabcoins = str(obj.get("tabcoins"))
        _owner_username = str(obj.get("owner_username"))
        _article_type = str(obj.get("article_type"))
        return TabNewsResponse(
            _id,
            _slug,
            _title,
            _status,
            _published_at,
            _tabcoins,
            _owner_username,
            _article_type,
        )


class TabNewsService:

    def __init__(self):
        self.base_url = "https://www.tabnews.com.br/api/v1"

    def most_relevant_posts(self) -> list[TabNewsResponse]:
        endpoint = "/contents?page=1&per_page=10&strategy=relevant"
        url = self.base_url + endpoint
        res = requests.get(url, timeout=30)
        if res.status_code < 200 or res.status_code >= 300:
            raise ConnectionRefusedError()

        articles_response = res.json()
        response = []
        for article in articles_response:
            tabnews_article = TabNewsResponse.from_dict(article)
            response.append(tabnews_article)

        return response

    def get_post_content(self, user: str, slug: str) -> str:
        endpoint = f"/contents/{user}/{slug}"
        url = self.base_url + endpoint
        res = requests.get(url, timeout=30)
        if res.status_code < 200 or res.status_code >= 300:
            raise ConnectionRefusedError()

        article_response = res.json()
        content = article_response.get("body", "")
        return content


if __name__ == "__main__":
    service = TabNewsService()
    posts = service.most_relevant_posts()
    for post in posts:
        print(f"Title: {post.title}, URL: {post.slug}")
