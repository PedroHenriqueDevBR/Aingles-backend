from sqlmodel import SQLModel, Field


class TokenReference(SQLModel, table=True):
    __tablename__ = 'token_reference'

    access_token: str = Field(primary_key=True)
    refresh_token: str = Field(primary_key=True)


class TokenBlacklist(SQLModel, table=True):
    __tablename__ = 'tokenblacklist'

    token: str = Field(primary_key=True)
