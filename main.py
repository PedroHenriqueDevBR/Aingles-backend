from fastapi import FastAPI
from routers import core, articles, card, auth
from services import supabase_service


app = FastAPI(
    title="Aingles API",
    description="API com sistema de autenticação integrado ao Supabase",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    supabase_service.create_db_and_tables()


# Public routes
app.include_router(
    core.router,
    prefix="",
    tags=["App"],
)

# Authentication routes
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Resource routes
app.include_router(
    articles.router,
    prefix="/article",
    tags=["Articles"],
)
app.include_router(
    card.router,
    prefix="/card",
    tags=["Cards"],
)
