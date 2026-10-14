import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()
@app.get("/hello")
def hello():
       return {"message": "Sveiki!"}

DB = str(Path(__file__).parent.parent / "game.db")


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


# создаём таблицу, если её нет
with db() as con:
    con.execute("""CREATE TABLE IF NOT EXISTS scores (
        player TEXT PRIMARY KEY,
        score  INTEGER NOT NULL
    )""")


class ScoreIn(BaseModel):
    player: str
    score: int          # если пришёл текст вместо числа -> автоматически 422


@app.get("/scores/top")                    # GET: "дай мне" -> 200
def top_scores():
    with db() as con:
        rows = con.execute(
            "SELECT player, score FROM scores ORDER BY score DESC LIMIT 10"
        ).fetchall()
    return [dict(r) for r in rows]


@app.get("/scores/{player}")               # 404, если такого игрока нет
def get_score(player: str):
    with db() as con:
        row = con.execute(
            "SELECT player, score FROM scores WHERE player = ?", (player,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Такого игрока нет")
    return dict(row)


@app.post("/scores", status_code=201)      # POST: "возьми это" -> 201 Created
def add_score(data: ScoreIn):
    name = data.player.strip()
    if not name or data.score < 0:
        raise HTTPException(status_code=400, detail="Пустое имя или отрицательный счёт")
    with db() as con:
        row = con.execute("SELECT score FROM scores WHERE player = ?", (name,)).fetchone()
        if row is None:
            con.execute("INSERT INTO scores VALUES (?, ?)", (name, data.score))
        elif data.score > row["score"]:    # обновляем, только если рекорд побит
            con.execute("UPDATE scores SET score = ? WHERE player = ?", (data.score, name))
    return {"player": name, "score": data.score}