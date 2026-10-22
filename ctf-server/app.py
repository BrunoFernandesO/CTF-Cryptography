"""CTF de Criptografia · WorkInTech (Axion) · V3.

Servidor Flask + SQLite. Roda no PythonAnywhere ou em qualquer máquina com Python 3.8+.
Veja o README.md para instalar, publicar e operar durante o evento."""
import os
import re
import secrets
import sqlite3
import time
from pathlib import Path

import click
from flask import Flask, g, jsonify, redirect, render_template, request, session

import puzzles

BASE = Path(__file__).resolve().parent
DB_PATH = os.environ.get("CTF_DB", str(BASE / "ctf.db"))
FREE_TOKEN = "LIVRE"
NICK_RE = re.compile(r"^[\w .\-]{2,24}$", re.UNICODE)
MAX_ATTEMPTS = 500  # tentativas para achar uma resposta ainda não usada por ninguém


def cooldown_for(wrong: int) -> int:
    """Espera (s) depois de um erro: cresce com os erros, para ninguém testar a lista inteira de chaves."""
    if wrong < 5:
        return 3
    if wrong < 10:
        return 30
    return 120


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
CREATE TABLE IF NOT EXISTS assignments (
    nick_key TEXT NOT NULL, level INTEGER NOT NULL, attempt INTEGER NOT NULL, flag_key TEXT NOT NULL,
    PRIMARY KEY (nick_key, level), UNIQUE (level, flag_key));
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


init_db()


# ---------- respostas únicas ----------
def assignment(nick_key: str, level: int) -> int:
    """Tentativa (semente) do puzzle deste jogador neste nível. Na primeira vez, procura uma tentativa cuja
    flag ninguém mais tenha; a restrição UNIQUE (level, flag_key) garante isso no banco."""
    conn = db()
    row = conn.execute("SELECT attempt FROM assignments WHERE nick_key=? AND level=?", (nick_key, level)).fetchone()
    if row:
        return row["attempt"]
    for attempt in range(MAX_ATTEMPTS):
        flag = puzzles.normalize_flag(puzzles.make_puzzle(SECRET, nick_key, level, attempt)["flag"])
        try:
            conn.execute("INSERT INTO assignments VALUES (?,?,?,?)", (nick_key, level, attempt, flag))
            conn.commit()
            return attempt
        except sqlite3.IntegrityError:
            conn.rollback()
            row = conn.execute("SELECT attempt FROM assignments WHERE nick_key=? AND level=?", (nick_key, level)).fetchone()
            if row:  # outro pedido do mesmo jogador chegou antes
                return row["attempt"]
    # Espaço esgotado (mais jogadores que respostas possíveis): aceita repetir, marcando a linha como duplicada.
    conn.execute("INSERT OR IGNORE INTO assignments VALUES (?,?,?,?)", (nick_key, level, 0, f"dup:{nick_key}"))
    conn.commit()
    return 0


def puzzle_for(nick_key: str, level: int) -> dict:
    return puzzles.make_puzzle(SECRET, nick_key, level, assignment(nick_key, level))


# ---------- util ----------
def current_player():
    nick_key, token = session.get("nick_key"), session.get("token")
    if not nick_key or not token:
        return None
    return db().execute("SELECT * FROM players WHERE nick_key=? AND token=?", (nick_key, token)).fetchone()


def solved_levels(nick_key):
    rows = db().execute("SELECT level FROM solves WHERE nick_key=?", (nick_key,)).fetchall()
    return {r["level"] for r in rows}


def player_payload(player):
    solved = solved_levels(player["nick_key"])
    levels = []
    for l in puzzles.LEVELS:
        pz = puzzle_for(player["nick_key"], l["id"])
        levels.append({
            "id": l["id"], "points": l["points"], "name": l["name"], "title": l["title"],
            "desc": l["desc"], "hint": l["hint"], "format": l["format"],
            "lines": [{"label": a, "value": b} for a, b in pz["lines"]],
            "solved": l["id"] in solved,
        })
    return {"nick": player["display"], "points": sum(puzzles.LEVEL_BY_ID[x]["points"] for x in solved), "levels": levels}


def board_rows():
    conn = db()
    players = conn.execute("SELECT nick_key, display, created FROM players").fetchall()
    solves = conn.execute("SELECT nick_key, level, ts FROM solves").fetchall()
    by_player = {}
    for s in solves:
        by_player.setdefault(s["nick_key"], []).append(s)
    rows = []
    for p in players:
        mine = by_player.get(p["nick_key"], [])
        rows.append({
            "nick": p["display"],
            "points": sum(puzzles.LEVEL_BY_ID[s["level"]]["points"] for s in mine),
            "levels": sorted(s["level"] for s in mine),
            "solved": len(mine),
            "_last": max((s["ts"] for s in mine), default=0.0),
            "_created": p["created"],
        })
    # Mais pontos primeiro; empate: quem chegou lá antes.
    rows.sort(key=lambda r: (-r["points"], r["_last"] if r["_last"] else float("inf"), r["_created"]))
    for r in rows:
        r.pop("_last"), r.pop("_created")
    return rows


# ---------- rotas ----------
@app.get("/")
def index():
    return render_template("index.html")


@app.get("/placar")
def scoreboard_page():
    return render_template("placar.html")


# Endereço curto para os computadores do laboratório: digitar /colab é mais fácil
# do que a URL do Google Drive. Pode ser trocado sem mexer no código (variável COLAB_URL).
COLAB_URL = os.environ.get(
    "COLAB_URL", "https://colab.research.google.com/drive/1N70OYpaif6YbzcAS442WMSWpG9n7g9t7")


@app.get("/colab", strict_slashes=False)
@app.get("/caderno", strict_slashes=False)
def colab():
    return redirect(COLAB_URL, code=302)


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
    if level not in puzzles.LEVEL_BY_ID:
        return jsonify({"error": "Nível inválido."}), 400
    flag = str(data.get("flag", ""))[:200]
    nick_key, conn = player["nick_key"], db()
    pts = puzzles.LEVEL_BY_ID[level]["points"]
    if level in solved_levels(nick_key):
        return jsonify({"ok": True, "message": "Você já resolveu este nível.", "points": 0})
    stats = conn.execute("SELECT COUNT(*) AS n, MAX(ts) AS t FROM attempts WHERE nick_key=? AND level=?",
                         (nick_key, level)).fetchone()
    now = time.time()
    if stats["t"]:
        wait = cooldown_for(stats["n"] - 1) - (now - stats["t"])
        if wait > 0:
            return jsonify({"ok": False, "wait": int(wait) + 1,
                            "message": f"Aguarde {int(wait) + 1} s para tentar de novo."}), 429
    if puzzles.flags_match(puzzle_for(nick_key, level)["flag"], flag):
        conn.execute("INSERT OR IGNORE INTO solves VALUES (?,?,?)", (nick_key, level, now))
        conn.commit()
        return jsonify({"ok": True, "message": f"Correto. +{pts} pontos.", "points": pts})
    conn.execute("INSERT INTO attempts VALUES (?,?,?)", (nick_key, level, now))
    conn.commit()
    wait = cooldown_for(stats["n"])
    return jsonify({"ok": False, "wait": wait,
                    "message": f"Flag incorreta. Confira o formato {puzzles.LEVEL_BY_ID[level]['format']}. Próxima tentativa em {wait} s."})


@app.get("/api/board")
def api_board():
    return jsonify(board_rows())


@app.get("/api/placar")
def api_placar():
    """Tudo o que o telão precisa numa só chamada: ranking, primeiros a resolver e últimos acertos."""
    conn = db()
    names = {r["nick_key"]: r["display"] for r in conn.execute("SELECT nick_key, display FROM players")}
    firsts = []
    for l in puzzles.LEVELS:
        r = conn.execute("SELECT nick_key, ts FROM solves WHERE level=? ORDER BY ts ASC LIMIT 1", (l["id"],)).fetchone()
        firsts.append({"level": l["id"], "name": l["name"], "nick": names.get(r["nick_key"]) if r else None,
                       "ts": r["ts"] if r else None})
    feed = [{"nick": names.get(r["nick_key"], r["nick_key"]), "level": r["level"],
             "name": puzzles.LEVEL_BY_ID[r["level"]]["name"], "ts": r["ts"]}
            for r in conn.execute("SELECT nick_key, level, ts FROM solves ORDER BY ts DESC LIMIT 8")]
    counts = {l["id"]: conn.execute("SELECT COUNT(*) FROM solves WHERE level=?", (l["id"],)).fetchone()[0]
              for l in puzzles.LEVELS}
    rows = board_rows()
    return jsonify({"rows": rows[:12], "players": len(rows), "firsts": firsts, "feed": feed,
                    "counts": [{"level": k, "name": puzzles.LEVEL_BY_ID[k]["name"], "solved": v} for k, v in counts.items()],
                    "now": time.time()})


# ---------- comandos do organizador ----------
@app.cli.command("liberar")
@click.argument("nick")
def liberar(nick):
    """Libera um apelido (o aluno perdeu o cookie e não consegue voltar). Mantém pontos e puzzles."""
    conn = sqlite3.connect(DB_PATH)
    n = conn.execute("UPDATE players SET token=? WHERE nick_key=?", (FREE_TOKEN, nick.strip().lower())).rowcount
    conn.commit()
    conn.close()
    click.echo("Apelido liberado: o próximo login com esse nome assume a conta." if n else "Apelido não encontrado.")


@app.cli.command("zerar")
@click.confirmation_option(prompt="Apagar todos os jogadores, pontos, tentativas e puzzles atribuídos?")
def zerar():
    """Apaga tudo (use antes de cada turma)."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("DELETE FROM attempts; DELETE FROM solves; DELETE FROM assignments; DELETE FROM players;")
    conn.commit()
    conn.close()
    click.echo("Banco zerado.")


@app.cli.command("respostas")
@click.argument("nick")
def respostas(nick):
    """Mostra o puzzle e a resposta de um jogador (para você conferir quando um aluno travar)."""
    nick_key = nick.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT level, attempt FROM assignments WHERE nick_key=? ORDER BY level", (nick_key,)).fetchall()
    conn.close()
    if not rows:
        click.echo("Apelido sem puzzles atribuídos.")
    for level, attempt in rows:
        pz = puzzles.make_puzzle(SECRET, nick_key, level, attempt)
        click.echo(f"Nível {level}: {pz['flag']}  {pz['solution']}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, threaded=True)
