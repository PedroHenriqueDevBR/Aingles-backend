from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content_url: str | None = Field(default='')
    title: str = Field(default="", index=True)
    content: str = Field(default="")
    author_id: str | None = Field(default=None, index=True)
