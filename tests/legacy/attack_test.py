import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ctf-server"))
from collections import Counter
from puzzles import make_puzzle, check_flag, ALPHA

# ===== código dos alunos (como aparecerá nos slides, TODOs preenchidos) =====
def cesar(texto, k):
    resultado = ""
    for c in texto.upper():
        if c.isalpha():
            n = ord(c) - ord("A")
            n = (n + k) % 26
            resultado += chr(n + ord("A"))
        else:
            resultado += c
    return resultado

def pontuacao(texto):
    return texto.count("A") + texto.count("E") + texto.count("O")

def quebrar_cesar(texto):
    melhor_k = 0
    melhor_pontos = 0
    for k in range(26):
        pontos = pontuacao(cesar(texto, -k))
        if pontos > melhor_pontos:
            melhor_k = k
            melhor_pontos = pontos
    return melhor_k

def ic(s):
    n = len(s)
    return sum(v * (v - 1) for v in Counter(s).values()) / (n * (n - 1))

def tamanho_chave(texto):
    melhor_m, melhor_ic = 1, 0
    for m in range(2, 9):
        colunas = [texto[i::m] for i in range(m)]
        media = sum(ic(c) for c in colunas) / m
        if media > melhor_ic + 0.005:
            melhor_m, melhor_ic = m, media
    return melhor_m

def quebrar_vigenere(texto, m):
    chave = ""
    for i in range(m):
        coluna = texto[i::m]
        k = quebrar_cesar(coluna)
        chave += chr(k + ord("A"))
    return chave

def fatorar(n):
    f = 2
    while n % f != 0:
        f += 1
    return f, n // f

secret = b"teste-secreto"
fail = {1: 0, 2: 0, 3: 0}
N = 400
bad_m = 0
for i in range(N):
    nick = f"aluno{i}"
    # nível 1
    pz = make_puzzle(secret, nick, 1)
    msg = pz["lines"][0][1]
    k = quebrar_cesar(msg)
    palavra = cesar(msg, -k).split()[-1]
    if not check_flag(secret, nick, 1, f"flag{{{palavra}}}"):
        fail[1] += 1
    # nível 2
    pz = make_puzzle(secret, nick, 2)
    texto = pz["lines"][0][1].replace(" ", "")
    real = pz["solution"]["key"]
    m = tamanho_chave(texto)
    chave = quebrar_vigenere(texto, m)
    # reduzir período
    for t in range(1, len(chave) + 1):
        if len(chave) % t == 0 and chave[:t] * (len(chave) // t) == chave:
            chave = chave[:t]; break
    if m % len(real) != 0 and m != len(real): bad_m += 1
    if not check_flag(secret, nick, 2, f"FLAG{{{chave}}}"):
        fail[2] += 1
        if fail[2] <= 5: print("L2 falhou", real, m, chave)
    # nível 3
    pz = make_puzzle(secret, nick, 3)
    d = {l: v for l, v in pz["lines"]}
    n, e, c = int(d["n"]), int(d["e"]), int(d["c (mensagem cifrada)"])
    p, q = fatorar(n)
    phi = (p - 1) * (q - 1)
    mm = pow(c, pow(e, -1, phi), n)
    if not check_flag(secret, nick, 3, f"FLAG{{{mm}}}"):
        fail[3] += 1
print("falhas em", N, "apelidos:", fail, "| m ruim:", bad_m)
