"""Geração dos puzzles do CTF (V2).

Cada puzzle é derivado de HMAC(segredo, "apelido:nível:tentativa"). O servidor guarda, por jogador e nível,
a tentativa usada e a flag correspondente, com a restrição de que duas pessoas nunca tenham a mesma flag
no mesmo nível (veja app.assignment). Sem o segredo do servidor, ninguém calcula a resposta.

Espaço de respostas por nível:
  1 · César     40 termos × 40 animais = 1.600 senhas diferentes (e k de 1 a 25)
  2 · Vigenère  131 chaves, todas testadas contra o ataque dos slides (IC + quebrar_cesar por coluna)
  3 · RSA       p e q primos entre 200 e 1000, m sorteado: praticamente infinitas respostas
"""
import hashlib
import hmac
import math
import random
import re

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Nível 1: a senha é TERMO-ANIMAL (sem acentos).
TERMS = [
    "MODULO", "CHAVE", "CIFRA", "PRIMO", "EUCLIDES", "FATOR", "SEGREDO", "ENIGMA", "TOKEN", "VETOR",
    "MATRIZ", "PONTEIRO", "ALGORITMO", "BINARIO", "RESTO", "DIVISOR", "EXPOENTE", "INVERSO", "CODIGO", "SENHA",
    "CADEADO", "ALFABETO", "MENSAGEM", "SINAL", "PACOTE", "CIRCUITO", "BYTE", "PIXEL", "KERNEL", "COMPILADOR",
    "FUNCAO", "VARIAVEL", "LACO", "PILHA", "FILA", "GRAFO", "ARVORE", "NUMERO", "TEOREMA", "LEMA",
]
ANIMALS = [
    "CORUJA", "LOBO", "GATO", "PANDA", "TUCANO", "ONCA", "CAPIVARA", "JACARE", "ARARA", "TATU",
    "LONTRA", "RAPOSA", "FALCAO", "POLVO", "BALEIA", "GOLFINHO", "TIGRE", "LEAO", "ZEBRA", "GIRAFA",
    "CAMELO", "CORVO", "PINGUIM", "TUBARAO", "COBRA", "SAPO", "MACACO", "CAVALO", "URSO", "ESQUILO",
    "GAVIAO", "PAVAO", "CISNE", "PATO", "FOCA", "LAGARTO", "MORCEGO", "BESOURO", "ABELHA", "FORMIGA",
]
CAESAR_TEXT = "PARABENS VOCE QUEBROU A CIFRA DE CESAR E A SENHA DESTE NIVEL E "

# Nível 2: 131 chaves de 3 a 7 letras, sem período menor e validadas contra o ataque dos slides.
VIG_KEYS = [
    "SOL", "MAR", "LUA", "CEU", "RIO", "PAZ", "LUZ", "FIM", "COR", "VOZ", "MEL", "SAL", "CHA", "REI", "DIA",
    "TERRA", "NUVEM", "PLANETA", "VENTO", "CHUVA", "AREIA", "PEDRA", "FOLHA", "FLOR", "RAIZ", "GALHO", "SEMENTE",
    "ONDA", "PRAIA", "ILHA", "LAGO", "MONTE", "VALE", "SERRA", "CAMPO", "ESTRADA", "PONTE", "TORRE", "CASTELO",
    "PORTA", "JANELA", "LIVRO", "CANETA", "PAPEL", "MESA", "CADEIRA", "RELOGIO", "ESPELHO", "CHAVE", "CORDA",
    "VELA", "MAPA", "BUSSOLA", "NAVIO", "REMO", "ANCORA", "VELEIRO", "FAROL", "COMETA", "ESTRELA", "GALAXIA",
    "ORBITA", "ECLIPSE", "AURORA", "TROVAO", "RAIO", "NEBLINA", "GEADA", "BRISA", "CRISTAL", "OURO", "PRATA",
    "COBRE", "FERRO", "BRONZE", "RUBI", "SAFIRA", "JADE", "OPALA", "QUARTZO", "MARMORE", "CARVAO", "VIOLINO",
    "PIANO", "FLAUTA", "TAMBOR", "HARPA", "SAMBA", "FORRO", "TANGO", "VALSA", "FREVO", "BOSSA", "PUDIM", "MANGA",
    "CAJU", "GOIABA", "AMORA", "LIMAO", "MELAO", "CACAU", "CAFE", "MILHO", "TRIGO", "ARROZ", "FEIJAO", "TIGRE",
    "LEAO", "ZEBRA", "PANDA", "URSO", "CISNE", "CORVO", "FALCAO", "TUCANO", "ARARA", "JAGUAR", "NORTE", "LESTE",
    "OESTE", "SUL", "VERAO", "OUTONO", "INVERNO", "NOITE", "TARDE", "MANHA", "SONHO", "SORTE", "ENIGMA", "SEGREDO",
]
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
        "id": 1, "points": 100, "name": "César", "title": "Nível 1 · César",
        "desc": "Cada letra foi deslocada k posições, a mesma em todo o texto. Descubra k, leia a mensagem e envie a senha.",
        "hint": "Só existem 25 deslocamentos úteis. Teste todos com o seu código e veja qual produz português.",
        "format": "FLAG{TERMO-ANIMAL}",
    },
    {
        "id": 2, "points": 200, "name": "Vigenère", "title": "Nível 2 · Vigenère",
        "desc": "O texto foi cifrado com uma chave curta que se repete. Descubra a chave.",
        "hint": "Tire os espaços. Ache o tamanho m da chave (índice de coincidência) e separe o texto em m colunas: cada uma é um César. Se a chave sair repetida (ex.: SOLSOL), a verdadeira é a menor.",
        "format": "FLAG{CHAVE}",
    },
    {
        "id": 3, "points": 300, "name": "RSA", "title": "Nível 3 · RSA pequeno",
        "desc": "Chaves de verdade têm 2048 bits. Esta é minúscula: fatore n, recupere a chave privada e decifre c.",
        "hint": "Fatore n por divisão sucessiva e calcule φ(n) = (p − 1)(q − 1). Depois d = pow(e, -1, phi) e m = pow(c, d, n).",
        "format": "FLAG{m}",
    },
]
LEVEL_BY_ID = {l["id"]: l for l in LEVELS}


def _rng(secret: bytes, nick: str, level: int, attempt: int) -> random.Random:
    msg = f"{nick.strip().lower()}:{level}:{attempt}".encode()
    digest = hmac.new(secret, msg, hashlib.sha256).digest()
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


def make_puzzle(secret: bytes, nick: str, level: int, attempt: int = 0) -> dict:
    """Devolve {'lines': [(rótulo, valor)], 'flag': str, 'solution': {...}}. A flag nunca vai para o cliente."""
    rng = _rng(secret, nick, level, attempt)
    if level == 1:
        k = rng.randint(1, 25)
        word = f"{rng.choice(TERMS)}-{rng.choice(ANIMALS)}"
        cipher = shift_text(CAESAR_TEXT + word, [k])
        return {"lines": [("Texto cifrado", cipher)], "flag": f"FLAG{{{word}}}", "solution": {"k": k, "senha": word}}
    if level == 2:
        key = rng.choice(VIG_KEYS)
        letters = "".join(c for c in VIG_TEXT if c in ALPHA)
        cipher = shift_text(letters, [ALPHA.index(c) for c in key])
        blocks = " ".join(cipher[i:i + 5] for i in range(0, len(cipher), 5))
        return {"lines": [("Texto cifrado (blocos de 5 letras)", blocks)], "flag": f"FLAG{{{key}}}", "solution": {"key": key}}
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
            "lines": [("n", str(n)), ("e", str(e)), ("c (mensagem cifrada)", str(c))],
            "flag": f"FLAG{{{m}}}", "solution": {"p": p, "q": q, "m": m},
        }
    raise ValueError("nível inválido")


def normalize_flag(s: str) -> str:
    """Aceita maiúsculas ou minúsculas, espaços, hífen ou sublinhado: FLAG{cifra coruja} = FLAG{CIFRA-CORUJA}."""
    return re.sub(r"[\s\-_]", "", s.upper())


def flags_match(expected: str, submitted: str) -> bool:
    return hmac.compare_digest(normalize_flag(submitted).encode(), normalize_flag(expected).encode())
