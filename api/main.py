import hashlib
import secrets
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from api.db import get_connection

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent          # это папка api/
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class UserIn(BaseModel):
    name: str
    password: str


class ScoreIn(BaseModel):
    score: int              # имени нет: его определяет токен


def player_by_token(conn, token):
    """Возвращает имя игрока по токену или бросает 401."""
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    row = conn.execute(
        "SELECT name FROM players WHERE token = ?", (token,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return row["name"]


@app.get("/hello")
def hello():
    return {"message": "Sveiki!"}


@app.get("/", response_class=HTMLResponse)
def leaderboard(request: Request):
    rows = top_scores()
    return templates.TemplateResponse(request, "leaderboard.html", {"rows": rows})


@app.get("/rules", response_class=HTMLResponse)
def rules(request: Request):
    return templates.TemplateResponse(request, "rules.html", {})


@app.get("/players/{name}", response_class=HTMLResponse)
def player_profile(request: Request, name: str):
    """HTML-страница профиля игрока со статистикой."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS games, MAX(score) AS best "
            "FROM scores WHERE player = ?", (name,)
        ).fetchone()

    if row["games"] == 0:
        raise HTTPException(status_code=404, detail="There is no such player")

    return templates.TemplateResponse(
        request,
        "player.html",
        {"player": name, "games": row["games"], "best": row["best"]},
    )


@app.post("/register", status_code=201)
def register(user: UserIn):
    name = user.name.strip()
    if not name or not user.password:
        raise HTTPException(status_code=400, detail="Empty name or password")
    with get_connection() as conn:
        exists = conn.execute(
            "SELECT 1 FROM players WHERE name = ?", (name,)
        ).fetchone()
        if exists:
            raise HTTPException(status_code=400, detail="The name is already taken")
        conn.execute(
            "INSERT INTO players (name, password_hash) VALUES (?, ?)",
            (name, hash_password(user.password)),
        )
    return {"name": name}


@app.post("/login")
def login(user: UserIn):
    name = user.name.strip()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM players WHERE name = ?", (name,)
        ).fetchone()
        if row is None or row["password_hash"] != hash_password(user.password):
            raise HTTPException(status_code=401, detail="Incorrect name or password")
        token = secrets.token_hex(16)
        conn.execute(
            "UPDATE players SET token = ? WHERE name = ?", (token, name)
        )
    return {"token": token}


@app.post("/scores", status_code=201)
def add_score(item: ScoreIn, token: str | None = Header(default=None)):
    if item.score < 0:
        raise HTTPException(status_code=400, detail="Negative balance")
    with get_connection() as conn:
        name = player_by_token(conn, token)
        conn.execute(
            "INSERT INTO scores (player, score) VALUES (?, ?)",
            (name, item.score),
        )
    return {"player": name, "score": item.score}


@app.get("/scores/top")
def top_scores():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT player, MAX(score) AS score FROM scores "
            "GROUP BY player ORDER BY score DESC LIMIT 10"
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/players/{name}/stats")
def player_stats(name: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS games, MAX(score) AS best "
            "FROM scores WHERE player = ?", (name,)
        ).fetchone()
    if row["games"] == 0:
        raise HTTPException(status_code=404, detail="There is no such player")
    return {"player": name, "games": row["games"], "best": row["best"]}


# Запуск (из корня проекта):
# source .venv_server/bin/activate
# python -m uvicorn api.main:app --reload