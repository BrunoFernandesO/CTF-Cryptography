"""CTF de Criptografia · WorkInTech (Axion) · V4.

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
from werkzeug.security import check_password_hash, generate_password_hash

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
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


init_db()


# ---------- níveis abertos/fechados (V4) ----------
# Fora da aula os níveis ficam fechados: a página não mostra o texto cifrado e o servidor recusa flags.
# O padrão é tudo fechado; o organizador abre cada nível na hora certa (console ou /organizador).
def get_setting(conn, key, default=None):
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


def set_setting(conn, key, value):
    conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                 (key, value))
    conn.commit()


def open_levels(conn=None) -> set:
    raw = get_setting(conn or db(), "open_levels", "")
    return {int(x) for x in raw.split(",") if x.strip().isdigit() and int(x) in puzzles.LEVEL_BY_ID}


def set_levels_open(conn, levels, is_open: bool) -> set:
    cur = open_levels(conn)
    cur = (cur | set(levels)) if is_open else (cur - set(levels))
    set_setting(conn, "open_levels", ",".join(str(x) for x in sorted(cur)))
    return cur


def parse_levels(spec) -> list:
    """'todos' | 1 | '2' | [1, 3] -> lista de níveis válidos; levanta ValueError se algo não existir."""
    if isinstance(spec, str) and spec.strip().lower() in ("todos", "all"):
        return [l["id"] for l in puzzles.LEVELS]
    items = spec if isinstance(spec, (list, tuple)) else [spec]
    out = []
    for it in items:
        n = int(it)
        if n not in puzzles.LEVEL_BY_ID:
            raise ValueError(n)
        out.append(n)
    return out


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
    opened = open_levels()
    levels = []
    for l in puzzles.LEVELS:
        item = {"id": l["id"], "points": l["points"], "name": l["name"], "title": l["title"],
                "desc": l["desc"], "format": l["format"], "solved": l["id"] in solved, "open": l["id"] in opened}
        if item["open"]:
            pz = puzzle_for(player["nick_key"], l["id"])
            item.update(hint=l["hint"], lines=[{"label": a, "value": b} for a, b in pz["lines"]])
        else:  # fechado: nem o texto cifrado nem a dica saem do servidor
            item.update(hint="", lines=[])
        levels.append(item)
    return {"nick": player["display"], "points": sum(puzzles.LEVEL_BY_ID[x]["points"] for x in solved),
            "levels": levels, "open": sorted(opened)}


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
    if level not in open_levels():
        return jsonify({"ok": False, "closed": True,
                        "message": "Este nível está fechado agora. Ele abre durante a aula."}), 403
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


@app.get("/api/estado")
def api_estado():
    """Consulta leve que a página do aluno repete a cada 10 s para saber quando um nível abriu."""
    return jsonify({"open": sorted(open_levels())})


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
    opened = open_levels()
    return jsonify({"rows": rows[:12], "players": len(rows), "firsts": firsts, "feed": feed,
                    "open": [puzzles.LEVEL_BY_ID[x]["name"] for x in sorted(opened)],
                    "counts": [{"level": k, "name": puzzles.LEVEL_BY_ID[k]["name"], "solved": v} for k, v in counts.items()],
                    "now": time.time()})


# ---------- painel do organizador (V4) ----------
LOGIN_FAILS = {}            # ip -> [falhas, bloqueado_até]
GLOBAL_FAILS = []           # horários das falhas recentes, de qualquer ip
MAX_FAILS_IP, LOCK_IP_S = 5, 300
MAX_FAILS_GLOBAL, WINDOW_GLOBAL_S = 20, 300


def client_ip():
    return (request.headers.get("X-Real-IP") or request.remote_addr or "?").strip()


def admin_required():
    if not session.get("admin"):
        return jsonify({"error": "Entre com a senha do organizador."}), 401
    if not request.method == "GET" and not request.is_json:
        return jsonify({"error": "Pedido inválido."}), 400
    return None


def admin_state():
    conn = db()
    opened = open_levels(conn)
    levels = []
    for l in puzzles.LEVELS:
        solved = conn.execute("SELECT COUNT(*) FROM solves WHERE level=?", (l["id"],)).fetchone()[0]
        levels.append({"id": l["id"], "name": l["name"], "points": l["points"], "open": l["id"] in opened,
                       "solved": solved})
    players = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    return {"levels": levels, "players": players, "open": sorted(opened)}


@app.get("/organizador")
def organizer_page():
    return render_template("organizador.html")


@app.post("/api/organizador/entrar")
def organizer_login():
    if not request.is_json:
        return jsonify({"error": "Pedido inválido."}), 400
    now, ip = time.time(), client_ip()
    fails, until = LOGIN_FAILS.get(ip, [0, 0])
    GLOBAL_FAILS[:] = [t for t in GLOBAL_FAILS if now - t < WINDOW_GLOBAL_S]
    if until > now:
        return jsonify({"error": f"Muitas tentativas. Espere {int(until - now) + 1} s."}), 429
    if len(GLOBAL_FAILS) >= MAX_FAILS_GLOBAL:
        return jsonify({"error": "Muitas tentativas erradas. Espere alguns minutos."}), 429
    stored = get_setting(db(), "admin_hash")
    if not stored:
        return jsonify({"error": "A senha ainda não foi criada. No console: flask --app app senha"}), 409
    senha = str((request.get_json(silent=True) or {}).get("senha", ""))[:200]
    if not check_password_hash(stored, senha):
        fails += 1
        GLOBAL_FAILS.append(now)
        LOGIN_FAILS[ip] = [0, now + LOCK_IP_S] if fails >= MAX_FAILS_IP else [fails, 0]
        return jsonify({"error": "Senha incorreta."}), 401
    LOGIN_FAILS.pop(ip, None)
    session.permanent = True
    session["admin"] = True
    return jsonify(admin_state())


@app.post("/api/organizador/sair")
def organizer_logout():
    session.pop("admin", None)
    return jsonify({"ok": True})


@app.get("/api/organizador/estado")
def organizer_state():
    denied = admin_required()
    return denied or jsonify(admin_state())


@app.post("/api/organizador/niveis")
def organizer_levels():
    denied = admin_required()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    try:
        levels = parse_levels(data.get("nivel"))
    except (TypeError, ValueError):
        return jsonify({"error": "Nível inválido."}), 400
    set_levels_open(db(), levels, bool(data.get("aberto")))
    return jsonify(admin_state())


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
    click.echo("Banco zerado (a senha e o estado dos níveis continuam):")
    _cli_status(conn)
    conn.close()


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


def _cli_levels(spec):
    try:
        return parse_levels(list(spec) if len(spec) > 1 else spec[0])
    except (TypeError, ValueError, IndexError):
        raise click.BadParameter("use 1, 2, 3 ou todos (ex.: abrir 2 3)")


def _cli_status(conn):
    opened = open_levels(conn)
    for l in puzzles.LEVELS:
        click.echo(f"  Nível {l['id']} ({l['name']}): {'ABERTO' if l['id'] in opened else 'fechado'}")


@app.cli.command("abrir")
@click.argument("niveis", nargs=-1, required=True)
def abrir(niveis):
    """Abre níveis: flask --app app abrir 1   |   abrir 2 3   |   abrir todos"""
    conn = sqlite3.connect(DB_PATH)
    set_levels_open(conn, _cli_levels(niveis), True)
    _cli_status(conn)
    conn.close()


@app.cli.command("fechar")
@click.argument("niveis", nargs=-1, required=True)
def fechar(niveis):
    """Fecha níveis: flask --app app fechar todos   |   fechar 3"""
    conn = sqlite3.connect(DB_PATH)
    set_levels_open(conn, _cli_levels(niveis), False)
    _cli_status(conn)
    conn.close()


@app.cli.command("status")
def status():
    """Mostra quais níveis estão abertos."""
    conn = sqlite3.connect(DB_PATH)
    _cli_status(conn)
    conn.close()


@app.cli.command("senha")
@click.password_option("--senha", prompt="Nova senha do organizador", confirmation_prompt="Repita a senha")
def senha(senha):
    """Cria ou troca a senha do painel /organizador (mínimo de 8 caracteres)."""
    if len(senha) < 8:
        raise click.BadParameter("use pelo menos 8 caracteres")
    conn = sqlite3.connect(DB_PATH)
    set_setting(conn, "admin_hash", generate_password_hash(senha))
    conn.close()
    click.echo("Senha salva. Entre em /organizador.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, threaded=True)
