"""Geração dos puzzles do CTF. Tudo é determinístico: mesmo apelido + mesmo nível = mesmo puzzle,
derivado de HMAC(segredo, apelido:nível). Sem o segredo do servidor, ninguém calcula a resposta."""
import hashlib
import hmac
import math
import random

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CODEWORDS = ["MODULO", "CHAVE", "CIFRA", "PRIMO", "EUCLIDES", "FATOR", "SEGREDO", "ENIGMA", "HASH", "TOKEN"]
VIG_KEYS = ["SOL", "MAR", "FOGO", "TERRA", "NUVEM", "PLANETA"]
CAESAR_TEXT = "PARABENS VOCE QUEBROU A CIFRA DE CESAR E A PALAVRA SECRETA DESTE NIVEL E "
VIG_TEXT = (
    "A CRIPTOGRAFIA PROTEGE NOSSAS CONVERSAS, NOSSAS SENHAS E NOSSOS PAGAMENTOS NA INTERNET. "
    "QUEM ENTENDE COMO ELA FUNCIONA TAMBEM ENTENDE COMO ELA PODE FALHAR, E ISSO AJUDA A CONSTRUIR "
    "SISTEMAS MAIS SEGUROS PARA TODOS. UMA CIFRA ANTIGA PODE PARECER FORTE ATE QUE ALGUEM "
    "DESCUBRA O PADRAO ESCONDIDO NAS LETRAS. POR ISSO ESTUDAR OS ATAQUES E TAO IMPORTANTE QUANTO "
    "ESTUDAR AS CIFRAS: SO QUEM SABE COMO UMA CHAVE PODE SER DESCOBERTA CONSEGUE ESCOLHER UMA CHAVE "
    "QUE RESISTA AO TEMPO, AOS COMPUTADORES E A CURIOSIDADE DE UMA TURMA INTEIRA DE ESTUDANTES."
)

LEVELS = [
    {
        "id": 1, "points": 100, "title": "Nível 1 · César",
        "desc": "Cada letra foi deslocada k posições, a mesma em todo o texto. Descubra k, leia a mensagem e envie a palavra secreta.",
        "hint": "Só existem 25 deslocamentos úteis. Teste todos com o seu código e veja qual produz português.",
    },
    {
        "id": 2, "points": 200, "title": "Nível 2 · Vigenère",
        "desc": "O texto foi cifrado com uma chave curta que se repete. Descubra a chave.",
        "hint": "Ache o tamanho m da chave (índice de coincidência). Separe o texto em m colunas: cada uma é um César. Se a chave sair repetida (ex.: SOLSOL), a verdadeira é a menor.",
    },
    {
        "id": 3, "points": 300, "title": "Nível 3 · RSA pequeno",
        "desc": "Chaves de verdade têm 2048 bits. Esta é minúscula: fatore n, recupere a chave privada e decifre c.",
        "hint": "Fatore n por divisão sucessiva e calcule φ(n) = (p − 1)(q − 1). Depois d = pow(e, -1, phi) e m = pow(c, d, n).",
    },
]


def _rng(secret: bytes, nick: str, level: int) -> random.Random:
    digest = hmac.new(secret, f"{nick.strip().lower()}:{level}".encode(), hashlib.sha256).digest()
    return random.Random(int.from_bytes(digest, "big"))


def shift_text(text: str, shifts) -> str:
    out, j = [], 0
    for ch in text:
        i = ALPHA.find(ch)
        if i < 0:
            out.append(ch)
            continue
        out.append(ALPHA[(i + shifts[j % len(shifts)]) % 26])
        j += 1
    return "".join(out)


def _primes_between(lo: int, hi: int):
    sieve = [True] * (hi + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(hi ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, hi + 1, i):
                sieve[j] = False
    return [i for i in range(lo, hi + 1) if sieve[i]]


_PRIMES = _primes_between(200, 1000)


def make_puzzle(secret: bytes, nick: str, level: int) -> dict:
    """Devolve {'lines': [(rótulo, valor)], 'flag': str}. A flag nunca deve ir para o cliente."""
    rng = _rng(secret, nick, level)
    if level == 1:
        k = rng.randint(1, 25)
        word = rng.choice(CODEWORDS)
        cipher = shift_text(CAESAR_TEXT + word, [k])
        return {"lines": [("Texto cifrado", cipher)], "flag": f"FLAG{{{word}}}", "solution": {"k": k}}
    if level == 2:
        key = rng.choice(VIG_KEYS)
        letters = "".join(c for c in VIG_TEXT if c in ALPHA)
        cipher = shift_text(letters, [ALPHA.index(c) for c in key])
        blocks = " ".join(cipher[i:i + 5] for i in range(0, len(cipher), 5))
        return {
            "lines": [("Texto cifrado (blocos de 5 letras)", blocks), ("Dica", "a flag é FLAG{CHAVE}, em maiúsculas")],
            "flag": f"FLAG{{{key}}}", "solution": {"key": key},
        }
    if level == 3:
        p = rng.choice(_PRIMES)
        q = rng.choice(_PRIMES)
        while q == p:
            q = rng.choice(_PRIMES)
        n, phi = p * q, (p - 1) * (q - 1)
        e = next(c for c in (17, 19, 23, 29, 31, 37) if math.gcd(c, phi) == 1)
        m = rng.randint(1000, n - 1)
        c = pow(m, e, n)
        return {
            "lines": [("n", str(n)), ("e", str(e)), ("c (mensagem cifrada)", str(c)),
                      ("Dica", "a flag é FLAG{m}, onde m é o número original")],
            "flag": f"FLAG{{{m}}}", "solution": {"p": p, "q": q, "m": m},
        }
    raise ValueError("nível inválido")


def check_flag(secret: bytes, nick: str, level: int, submitted: str) -> bool:
    expected = make_puzzle(secret, nick, level)["flag"].upper()
    return hmac.compare_digest(submitted.strip().upper().encode(), expected.encode())
