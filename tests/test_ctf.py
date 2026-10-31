"""Tests for the CTF server as used in class (V4.3)."""
import sqlite3

import pytest

import solucoes
from conftest import flag_of, login


# ---------- unique answers ----------
def test_sixty_students_get_sixty_different_answers(server, open_all):
    nicks = [f"aluno{i:02d}" for i in range(60)]
    for nick in nicks:
        assert login(server.app.test_client(), nick).status_code == 200
    for level in (1, 2, 3):
        flags = [server.puzzles.normalize_flag(flag_of(server, n, level)) for n in nicks]
        assert len(set(flags)) == 60, f"level {level} repeated an answer"


def test_answer_space_sizes(server):
    assert len(server.puzzles.TERMS) * len(server.puzzles.ANIMALS) == 1600
    assert len(server.puzzles.VIG_KEYS) == 131


def test_class_attacks_solve_every_level(server, open_all):
    """The functions from reference/solucoes.py (the slide code with the TODOs filled in) solve all three levels."""
    for i in range(5):
        c = server.app.test_client()
        levels = {l["id"]: [x["value"] for x in l["lines"]] for l in login(c, f"turma{i}").get_json()["levels"]}

        ct = levels[1][0]
        senha = solucoes.cesar(ct, -solucoes.quebrar_cesar(ct)).split()[-1]

        t2 = levels[2][0].replace(" ", "")
        chave = solucoes.quebrar_vigenere(t2, solucoes.tamanho_chave(t2))
        for t in range(1, len(chave) + 1):  # se a chave sair repetida (SOLSOL), vale a menor
            if len(chave) % t == 0 and chave[:t] * (len(chave) // t) == chave:
                chave = chave[:t]
                break

        n, e, cifra = (int(v) for v in levels[3])
        p, q = solucoes.fatorar(n)
        m = pow(cifra, pow(e, -1, (p - 1) * (q - 1)), n)

        for level, flag in ((1, f"FLAG{{{senha}}}"), (2, f"FLAG{{{chave}}}"), (3, f"FLAG{{{m}}}")):
            assert c.post("/api/submit", json={"level": level, "flag": flag}).get_json()["ok"]
        assert c.get("/api/me").get_json()["points"] == 600


def test_flag_format_is_tolerant(server, open_all):
    c = server.app.test_client()
    login(c, "formato")
    flag = flag_of(server, "formato", 1)  # FLAG{TERMO-ANIMAL}
    sloppy = flag.lower().replace("-", " ")
    assert c.post("/api/submit", json={"level": 1, "flag": sloppy}).get_json()["ok"]


# ---------- cooldowns ----------
def test_cooldown_steps():
    import app
    assert [app.cooldown_for(n) for n in range(12)] == [3] * 5 + [30] * 5 + [120] * 2


def test_wrong_flags_wait_longer_and_longer(server, open_all, clock):
    c = server.app.test_client()
    login(c, "chutador")
    waits = []
    for _ in range(11):
        r = c.post("/api/submit", json={"level": 2, "flag": "FLAG{ERRADA}"})
        assert r.status_code == 200 and not r.get_json()["ok"]
        waits.append(r.get_json()["wait"])
        early = c.post("/api/submit", json={"level": 2, "flag": "FLAG{ERRADA}"})
        assert early.status_code == 429  # tried again before the wait ended
        clock.advance(waits[-1])
    assert waits == [3] * 5 + [30] * 5 + [120]


def test_cooldown_is_per_level(server, open_all, clock):
    c = server.app.test_client()
    login(c, "dois-niveis")
    c.post("/api/submit", json={"level": 1, "flag": "FLAG{X}"})
    assert c.post("/api/submit", json={"level": 1, "flag": "FLAG{X}"}).status_code == 429
    assert c.post("/api/submit", json={"level": 2, "flag": "FLAG{X}"}).status_code == 200


# ---------- levels open only during class ----------
def test_closed_level_hides_data_and_rejects_flags(server):
    c = server.app.test_client()
    me = login(c, "em-casa").get_json()
    for level in me["levels"]:
        assert level["open"] is False and level["lines"] == [] and level["hint"] == ""
    r = c.post("/api/submit", json={"level": 1, "flag": flag_of(server, "em-casa", 1)})
    assert r.status_code == 403 and r.get_json()["closed"]
    assert c.get("/api/me").get_json()["points"] == 0


def test_organizer_opens_a_level(server):
    runner = server.app.test_cli_runner()
    assert "Senha salva" in runner.invoke(args=["senha", "--senha", "senha-do-teste"]).output
    org = server.app.test_client()
    assert org.post("/api/organizador/entrar", json={"senha": "errada"}).status_code == 401
    assert org.post("/api/organizador/entrar", json={"senha": "senha-do-teste"}).status_code == 200
    assert org.post("/api/organizador/niveis", json={"nivel": 1, "aberto": True}).get_json()["open"] == [1]

    aluno = server.app.test_client()
    levels = {l["id"]: l for l in login(aluno, "na-aula").get_json()["levels"]}
    assert levels[1]["open"] and levels[1]["lines"]
    assert not levels[2]["open"] and levels[2]["lines"] == []
    assert aluno.get("/api/estado").get_json() == {"open": [1]}


def test_organizer_panel_needs_the_password(server):
    c = server.app.test_client()
    assert c.post("/api/organizador/niveis", json={"nivel": "todos", "aberto": True}).status_code == 401
    assert c.get("/api/estado").get_json() == {"open": []}


# ---------- nickname + PIN accounts ----------
def test_new_account_needs_a_four_digit_pin(server):
    c = server.app.test_client()
    assert login(c, "novo", pin="").status_code == 400
    assert login(c, "novo", pin="12a4").status_code == 400
    r = login(c, "novo", pin="4321")
    assert r.status_code == 200 and r.get_json()["created"]


def test_pin_brings_the_account_back_on_another_computer(server, open_all):
    dia1 = server.app.test_client()
    login(dia1, "Maria", pin="2468")
    dia1.post("/api/submit", json={"level": 1, "flag": flag_of(server, "maria", 1)})

    dia2 = server.app.test_client()  # another lab computer, no cookie
    assert login(dia2, "maria", pin="0000").status_code == 401
    me = login(dia2, "maria", pin="2468").get_json()
    assert me["nick"] == "Maria" and me["points"] == 100 and not me["created"]


def test_same_browser_gets_back_in_without_pin(server):
    c = server.app.test_client()
    login(c, "cookie", pin="1111")
    assert login(c, "cookie", pin="").status_code == 200


def test_five_wrong_pins_lock_the_nickname_for_five_minutes(server, clock):
    login(server.app.test_client(), "alvo", pin="1357")
    atacante = server.app.test_client()
    codes = [login(atacante, "alvo", pin=f"{i:04d}").status_code for i in range(5)]
    assert codes == [401, 401, 401, 401, 429]

    dono = server.app.test_client()
    assert login(dono, "alvo", pin="1357").status_code == 429  # locked even with the right PIN
    clock.advance(server.PIN_LOCK_S - 1)
    assert login(dono, "alvo", pin="1357").status_code == 429
    clock.advance(2)
    assert login(dono, "alvo", pin="1357").status_code == 200


def test_right_pin_resets_the_failure_count(server):
    login(server.app.test_client(), "distraido", pin="1357")
    c = server.app.test_client()
    for _ in range(4):
        assert login(c, "distraido", pin="0000").status_code == 401
    assert login(c, "distraido", pin="1357").status_code == 200
    c2 = server.app.test_client()
    for _ in range(4):
        assert login(c2, "distraido", pin="0000").status_code == 401  # four more, still not locked


# ---------- liberar ----------
def test_liberar_keeps_points_and_puzzles(server, open_all):
    antigo = server.app.test_client()
    me = login(antigo, "Esquecido", pin="1212").get_json()
    puzzles_before = {l["id"]: l["lines"] for l in me["levels"]}
    antigo.post("/api/submit", json={"level": 1, "flag": flag_of(server, "esquecido", 1)})

    out = server.app.test_cli_runner().invoke(args=["liberar", "esquecido"]).output
    assert "Esquecido liberado" in out
    assert antigo.get("/api/me").get_json() == {"logged_in": False}  # the old session no longer works

    novo = server.app.test_client()
    assert login(novo, "esquecido", pin="").status_code == 400  # must choose a new PIN
    me = login(novo, "esquecido", pin="3434").get_json()
    assert me["points"] == 100
    assert {l["id"]: l["lines"] for l in me["levels"]} == puzzles_before
    assert login(server.app.test_client(), "esquecido", pin="1212").status_code == 401  # old PIN is gone
    assert login(server.app.test_client(), "esquecido", pin="3434").status_code == 200


def test_liberar_from_the_organizer_panel(server):
    server.app.test_cli_runner().invoke(args=["senha", "--senha", "senha-do-teste"])
    login(server.app.test_client(), "painel", pin="5555")
    org = server.app.test_client()
    org.post("/api/organizador/entrar", json={"senha": "senha-do-teste"})
    assert org.post("/api/organizador/liberar", json={"apelido": "PAINEL"}).status_code == 200
    assert org.post("/api/organizador/liberar", json={"apelido": "ninguem"}).status_code == 404
    assert login(server.app.test_client(), "painel", pin="6666").status_code == 200


def test_liberar_unknown_nickname(server):
    assert "não encontrado" in server.app.test_cli_runner().invoke(args=["liberar", "fantasma"]).output


# ---------- old database ----------
def test_old_database_is_migrated_without_losing_data(server, open_all):
    """A V2-V4.2 database (players without PIN columns) is upgraded in place by init_db()."""
    conn = sqlite3.connect(server.DB_PATH)
    conn.executescript("""
        DROP TABLE players;
        CREATE TABLE players (nick_key TEXT PRIMARY KEY, display TEXT NOT NULL, token TEXT NOT NULL, created REAL NOT NULL);
        INSERT INTO players VALUES ('veterano', 'Veterano', 'token-antigo', 1.0);
        INSERT INTO solves VALUES ('veterano', 1, 2.0);
    """)
    conn.commit()
    conn.close()

    server.init_db()

    conn = sqlite3.connect(server.DB_PATH)
    columns = {r[1] for r in conn.execute("PRAGMA table_info(players)")}
    row = conn.execute("SELECT display, token, pin_hash, pin_fails, pin_lock FROM players").fetchone()
    conn.close()
    assert {"pin_hash", "pin_fails", "pin_lock"} <= columns
    assert row == ("Veterano", "token-antigo", None, 0, 0)

    # From another computer an old account without a PIN cannot be claimed by guessing.
    assert login(server.app.test_client(), "veterano", pin="1234").status_code == 409

    # From the browser that already holds its session, the first login records a PIN.
    c = server.app.test_client()
    with c.session_transaction() as s:
        s["nick_key"], s["token"] = "veterano", "token-antigo"
    me = login(c, "veterano", pin="9090").get_json()
    assert me["points"] == 100
    assert login(server.app.test_client(), "veterano", pin="9090").status_code == 200


def test_migration_is_idempotent(server):
    server.init_db()
    server.init_db()
    conn = sqlite3.connect(server.DB_PATH)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(players)")]
    conn.close()
    assert cols.count("pin_hash") == 1


# ---------- pages ----------
@pytest.mark.parametrize("path, code", [
    ("/", 200), ("/placar", 200), ("/organizador", 200), ("/api/placar", 200), ("/api/estado", 200),
    ("/colab", 302), ("/caderno", 302), ("/desafio", 302), ("/colab-desafio", 302),
])
def test_routes(server, path, code):
    assert server.app.test_client().get(path).status_code == code
