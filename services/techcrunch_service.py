import requests
from bs4 import BeautifulSoup


class TechCrunchResponse:

    def __init__(
        self,
        category: str,
        title: str,
        url: str,
        slug: str,
        published_at: str,
        owner_username: str,
        content: str = None,
    ):
        self.category = category
        self.title = title
        self.url = url
        self.slug = slug
        self.published_at = published_at
        self.owner_username = owner_username
        self.content = content

    @staticmethod
    def from_dict(obj: dict) -> "TechCrunchResponse":
        _category = str(obj.get("category"))
        _title = str(obj.get("title"))
        _url = str(obj.get("url"))
        _slug = str(obj.get("slug"))
        _published_at = str(obj.get("published_at"))
        _owner_username = str(obj.get("owner_username"))
        _content = str(obj.get("content"))
        return TechCrunchResponse(
            _category,
            _title,
            _url,
            _slug,
            _published_at,
            _owner_username,
            content=_content,
        )

    def to_json(self) -> dict:
        return {
            "category": self.category,
            "title": self.title,
            "url": self.url,
            "slug": self.slug,
            "published_at": self.published_at,
            "owner_username": self.owner_username,
            "content": self.content,
        }


class TechCrunchService:

    def __init__(self):
        self.base_url = "https://techcrunch.com"

    def latest_posts(self) -> list[TechCrunchResponse]:
        url = self.base_url + "/latest/"
        res = requests.get(url, timeout=30)
        if res.status_code < 200 or res.status_code >= 300:
            raise ConnectionRefusedError()

        soup = BeautifulSoup(res.content, "html.parser")
        cards = soup.find_all("div", class_="loop-card--post-type-post")
        response = []

        for card in cards:
            # Title
            title_tag = card.find("a", class_="loop-card__title-link")
            title = title_tag.get_text(strip=True) if title_tag else "No Title"

            # URL and Slug
            link_tag = card.find("a", class_="loop-card__title-link")
            url = (
                link_tag["href"] if link_tag and "href" in link_tag.attrs else "No URL"
            )
            slug = url.split("/")[-2] if url != "No URL" else "No Slug"

            # Category
            category_tag = card.find("a", class_="loop-card__cat")
            category = (
                category_tag.get_text(strip=True) if category_tag else "No Category"
            )

            # Published At
            published_at_tag = card.find("time", class_="loop-card__time")
            published_at = (
                published_at_tag["datetime"]
                if published_at_tag and "datetime" in published_at_tag.attrs
                else "No Date"
            )

            # Owner Username
            owner_username_tag = card.find("a", class_="loop-card__author")
            owner_username = (
                owner_username_tag.get_text(strip=True)
                if owner_username_tag
                else "No Author"
            )

            techcrunch_response = TechCrunchResponse(
                category=category,
                title=title,
                url=url,
                slug=slug,
                published_at=published_at,
                owner_username=owner_username,
            )
            response.append(techcrunch_response)

        return response

    def get_post_content(self, url: str) -> str:
        res = requests.get(url, timeout=30)
        if res.status_code < 200 or res.status_code >= 300:
            raise ConnectionRefusedError()

        soup = BeautifulSoup(res.content, "html.parser")
        content_tag = soup.find("div", class_="entry-content")

        if not content_tag:
            return "No Content"

        markdown_content = []

        for element in content_tag.descendants:
            if element.name == "h1":
                markdown_content.append(f"\n# {element.get_text(strip=True)}\n")
            elif element.name == "h2":
                markdown_content.append(f"\n## {element.get_text(strip=True)}\n")
            elif element.name == "h3":
                markdown_content.append(f"\n### {element.get_text(strip=True)}\n")
            elif element.name == "h4" or element.name == "h5" or element.name == "h6":
                markdown_content.append(f"\n#### {element.get_text(strip=True)}\n")
            elif element.name == "p":
                text = element.get_text(strip=True)
                if text:
                    markdown_content.append(f"{text}\n\n")
            elif element.name == "a" and element.get("href"):
                markdown_content.append(
                    f"[{element.get_text(strip=True)}]({element['href']})"
                )
            elif element.name == "strong" or element.name == "b":
                markdown_content.append(f"**{element.get_text(strip=True)}**")
            elif element.name == "em" or element.name == "i":
                markdown_content.append(f"*{element.get_text(strip=True)}*")
            elif element.name == "li":
                markdown_content.append(f"- {element.get_text(strip=True)}\n")

        return "".join(markdown_content).strip()


if __name__ == "__main__":
    service = TechCrunchService()
    posts = service.latest_posts()

    for post in posts:
        print(post.url)

    # resp = service.get_post_content("https://techcrunch.com/2025/10/09/google-ramps-up-its-ai-in-the-workplace-ambitions-with-gemini-enterprise/")
    # print(resp)
