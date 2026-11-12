import secrets
import string
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from app import db

ALPHABET = string.ascii_letters + string.digits


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init()
    yield


app = FastAPI(title="Shortly", description="A tiny URL shortener API", version="1.0.0", lifespan=lifespan)


class LinkIn(BaseModel):
    url: HttpUrl


class LinkOut(BaseModel):
    code: str
    url: str
    short_url: str


class Stats(BaseModel):
    code: str
    url: str
    clicks: int
    created_at: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/links", response_model=LinkOut, status_code=201)
def create_link(payload: LinkIn, request: Request):
    url = str(payload.url)
    with db.connect() as conn:
        while True:
            code = "".join(secrets.choice(ALPHABET) for _ in range(6))
            if not conn.execute("SELECT 1 FROM links WHERE code = ?", (code,)).fetchone():
                break
        conn.execute("INSERT INTO links (code, url) VALUES (?, ?)", (code, url))
    return LinkOut(code=code, url=url, short_url=f"{request.base_url}{code}")


@app.get("/links/{code}/stats", response_model=Stats)
def link_stats(code: str):
    with db.connect() as conn:
        row = conn.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
    if not row:
        raise HTTPException(404, "Link not found")
    return Stats(**dict(row))


@app.get("/{code}")
def redirect(code: str):
    with db.connect() as conn:
        row = conn.execute("SELECT url FROM links WHERE code = ?", (code,)).fetchone()
        if not row:
            raise HTTPException(404, "Link not found")
        conn.execute("UPDATE links SET clicks = clicks + 1 WHERE code = ?", (code,))
    return RedirectResponse(row["url"])
