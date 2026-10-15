from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.db import get_connection

app = FastAPI()


@app.get("/hello")
def hello():
    return {"message": "Sveiki!"}


class ScoreIn(BaseModel):
    player: str
    score: int          # текст вместо числа -> автоматически 422


@app.get("/scores/top")
def top_scores():
    with get_connection() as con:
        rows = con.execute(
            "SELECT player, score FROM scores ORDER BY score DESC LIMIT 10"
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/scores/{player}")
def get_score(player: str):
    with get_connection() as con:
        row = con.execute(
            "SELECT player, score FROM scores WHERE player = ?", (player,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Такого игрока нет")
    return dict(row)


@app.post("/scores", status_code=201)
def add_score(data: ScoreIn):
    name = data.player.strip()
    if not name or data.score < 0:
        raise HTTPException(status_code=400, detail="Пустое имя или отрицательный счёт")
    with get_connection() as con:
        row = con.execute(
            "SELECT score FROM scores WHERE player = ?", (name,)
        ).fetchone()
        if row is None:                      # новый игрок -> добавляем
            con.execute(
                "INSERT INTO scores (player, score) VALUES (?, ?)",
                (name, data.score),
            )
        elif data.score > row["score"]:      # рекорд побит -> обновляем
            con.execute(
                "UPDATE scores SET score = ? WHERE player = ?",
                (data.score, name),
            )
    best = data.score if row is None else max(row["score"], data.score)
    return {"player": name, "score": best}