"""CTF de Criptografia · WorkInTech.
Servidor Flask + SQLite para rodar no notebook do palestrante, na rede do laboratório.
Veja o README.md para as instruções de execução."""
import os
import re
import secrets
import sqlite3
import time
from pathlib import Path

import click
from flask import Flask, g, jsonify, render_template, request, session

import puzzles

BASE = Path(__file__).resolve().parent
DB_PATH = os.environ.get("CTF_DB", str(BASE / "ctf.db"))
FREE_TOKEN = "LIVRE"
WRONG_COOLDOWN = 3  # segundos entre tentativas erradas, por jogador e por nível
NICK_RE = re.compile(r"^[\w .\-]{2,24}$", re.UNICODE)


def load_secret() -> bytes:
    """Segredo persistente: reiniciar o servidor não muda os puzzles de ninguém."""
    env = os.environ.get("CTF_SECRET")
    if env:
        return env.encode()
    f = BASE / "secret.key"
    if not f.exists():
        f.write_text(secrets.token_hex(32))
    return f.read_text().strip().encode()


SECRET = load_secret()
app = Flask(__name__)
app.secret_key = SECRET
app.config.update(SESSION_COOKIE_SAMESITE="Lax", PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 3)


# ---------- banco ----------
def db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    nick_key TEXT PRIMARY KEY, display TEXT NOT NULL, token TEXT NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS solves (
    nick_key TEXT NOT NULL, level INTEGER NOT NULL, ts REAL NOT NULL, PRIMARY KEY (nick_key, level));
CREATE TABLE IF NOT EXISTS attempts (
    nick_key TEXT NOT NULL, level INTEGER NOT NULL, ts REAL NOT NULL);
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


init_db()


# ---------- util ----------
LEVEL_BY_ID = {l["id"]: l for l in puzzles.LEVELS}


def current_player():
    nick_key, token = session.get("nick_key"), session.get("token")
    if not nick_key or not token:
        return None
    row = db().execute("SELECT * FROM players WHERE nick_key=? AND token=?", (nick_key, token)).fetchone()
    return row


def solved_levels(nick_key):
    rows = db().execute("SELECT level FROM solves WHERE nick_key=?", (nick_key,)).fetchall()
    return {r["level"] for r in rows}


def player_payload(player):
    solved = solved_levels(player["nick_key"])
    levels = []
    for l in puzzles.LEVELS:
        pz = puzzles.make_puzzle(SECRET, player["nick_key"], l["id"])
        levels.append({
            "id": l["id"], "points": l["points"], "title": l["title"], "desc": l["desc"], "hint": l["hint"],
            "lines": [{"label": a, "value": b} for a, b in pz["lines"]],
            "solved": l["id"] in solved,
        })
    return {"nick": player["display"], "points": sum(LEVEL_BY_ID[x]["points"] for x in solved), "levels": levels}


def board_rows():
    rows = db().execute(
        """SELECT p.display AS nick, COALESCE(SUM(CASE s.level WHEN 1 THEN 100 WHEN 2 THEN 200 WHEN 3 THEN 300 END), 0) AS pts,
                  COUNT(s.level) AS n, COALESCE(MAX(s.ts), 0) AS last_ts
           FROM players p LEFT JOIN solves s ON s.nick_key = p.nick_key
           GROUP BY p.nick_key ORDER BY pts DESC, last_ts ASC, p.created ASC""").fetchall()
    return [{"nick": r["nick"], "points": r["pts"], "solved": r["n"]} for r in rows]


# ---------- rotas ----------
@app.get("/")
def index():
    return render_template("index.html")


@app.get("/placar")
def scoreboard_page():
    return render_template("placar.html")


@app.get("/api/me")
def api_me():
    player = current_player()
    if not player:
        return jsonify({"logged_in": False})
    return jsonify({"logged_in": True, **player_payload(player)})


@app.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    display = str(data.get("nick", "")).strip()
    if not NICK_RE.match(display):
        return jsonify({"error": "Use de 2 a 24 caracteres: letras, números, espaço, _ , . ou -."}), 400
    nick_key = display.lower()
    conn = db()
    row = conn.execute("SELECT * FROM players WHERE nick_key=?", (nick_key,)).fetchone()
    if row is None:
        token = secrets.token_hex(16)
        conn.execute("INSERT INTO players VALUES (?,?,?,?)", (nick_key, display, token, time.time()))
        conn.commit()
    elif session.get("nick_key") == nick_key and session.get("token") == row["token"]:
        token = row["token"]
    elif row["token"] == FREE_TOKEN:  # liberado pelo organizador: quem entrar primeiro assume
        token = secrets.token_hex(16)
        conn.execute("UPDATE players SET token=? WHERE nick_key=?", (token, nick_key))
        conn.commit()
    else:
        return jsonify({"error": "Esse apelido já está em uso. Escolha outro."}), 409
    session.permanent = True
    session["nick_key"], session["token"] = nick_key, token
    player = conn.execute("SELECT * FROM players WHERE nick_key=?", (nick_key,)).fetchone()
    return jsonify({"logged_in": True, **player_payload(player)})


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.post("/api/submit")
def api_submit():
    player = current_player()
    if not player:
        return jsonify({"error": "Faça login primeiro."}), 401
    data = request.get_json(silent=True) or {}
    try:
        level = int(data.get("level"))
    except (TypeError, ValueError):
        return jsonify({"error": "Nível inválido."}), 400
    if level not in LEVEL_BY_ID:
        return jsonify({"error": "Nível inválido."}), 400
    flag = str(data.get("flag", ""))[:200]
    nick_key, conn = player["nick_key"], db()
    if level in solved_levels(nick_key):
        return jsonify({"ok": True, "message": "Você já resolveu este nível.", "points": LEVEL_BY_ID[level]["points"]})
    last = conn.execute("SELECT MAX(ts) AS t FROM attempts WHERE nick_key=? AND level=?", (nick_key, level)).fetchone()["t"]
    now = time.time()
    if last and now - last < WRONG_COOLDOWN:
        wait = int(WRONG_COOLDOWN - (now - last)) + 1
        return jsonify({"ok": False, "message": f"Calma! Aguarde {wait}s para tentar de novo."}), 429
    if puzzles.check_flag(SECRET, nick_key, level, flag):
        conn.execute("INSERT OR IGNORE INTO solves VALUES (?,?,?)", (nick_key, level, now))
        conn.commit()
        pts = LEVEL_BY_ID[level]["points"]
        return jsonify({"ok": True, "message": f"Correto! +{pts} pontos.", "points": pts})
    conn.execute("INSERT INTO attempts VALUES (?,?,?)", (nick_key, level, now))
    conn.commit()
    return jsonify({"ok": False, "message": "Flag incorreta. Confira o formato FLAG{...} e tente de novo."})


@app.get("/api/board")
def api_board():
    return jsonify(board_rows())


# ---------- comandos do organizador ----------
@app.cli.command("liberar")
@click.argument("nick")
def liberar(nick):
    """Libera um apelido (o aluno perdeu o cookie e não consegue voltar). Mantém os pontos."""
    conn = sqlite3.connect(DB_PATH)
    n = conn.execute("UPDATE players SET token=? WHERE nick_key=?", (FREE_TOKEN, nick.strip().lower())).rowcount
    conn.commit()
    conn.close()
    click.echo("Apelido liberado: o próximo login com esse nome assume a conta." if n else "Apelido não encontrado.")


@app.cli.command("zerar")
@click.confirmation_option(prompt="Apagar todos os jogadores, pontos e tentativas?")
def zerar():
    """Apaga tudo (use antes de cada turma). Os puzzles não mudam, pois dependem do segredo."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("DELETE FROM attempts; DELETE FROM solves; DELETE FROM players;")
    conn.commit()
    conn.close()
    click.echo("Banco zerado.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, threaded=True)
