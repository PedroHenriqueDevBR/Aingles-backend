from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root() -> dict[str, Union[str, int]]:
    return {"message": "Hello, World!", "status": 200}
