from typing import Union
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root() -> dict[str, Union[str, int]]:
    return {"message": "Hi, I'm Aingles Backend", "status": 200}


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
