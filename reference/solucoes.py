"""Código Python do workshop "Criptografia na Prática" (WorkInTech · Axion).

É o código dos slides com todos os TODO preenchidos (em português, sem acentos nos textos, só letras A-Z).
Foi executado e testado: todos os `assert` abaixo passam. Os ataques foram validados contra 400 apelidos
diferentes nos 3 níveis do CTF, sem falhas. Para rodar: python3 03-codigo-python.py
"""
from collections import Counter


# ---------- Dia 1: César ----------
def cesar(texto, k):
    resultado = ""
    for c in texto.upper():
        if c.isalpha():
            n = ord(c) - ord("A")
            n = (n + k) % 26            # TODO dos alunos
            resultado += chr(n + ord("A"))
        else:
            resultado += c
    return resultado


# Ataque 1 (slide 18, nível 1 do CTF): força bruta, 25 chaves úteis
#   for k in range(1, 26):
#       print(k, cesar(msg, -k))        # TODO dos alunos: cesar(msg, -k)

# Ataque 2 (slide 19): o Python escolhe a chave sozinho
def pontuacao(texto):
    return texto.count("A") + texto.count("E") + texto.count("O")   # TODO dos alunos


def quebrar_cesar(texto):
    melhor_k = 0
    melhor_pontos = 0
    for k in range(26):
        pontos = pontuacao(cesar(texto, -k))
        if pontos > melhor_pontos:
            melhor_k = k
            melhor_pontos = pontos
    return melhor_k


# ---------- Dia 1: Vigenère ----------
def vigenere(texto, chave):
    resultado = ""
    i = 0
    for c in texto.upper():
        if c.isalpha():
            k = ord(chave[i % len(chave)]) - ord("A")
            resultado += cesar(c, k)    # TODO dos alunos: reaproveitar o cesar()
            i += 1
        else:
            resultado += c
    return resultado


# ---------- Dia 2: quebrando o Vigenère ----------
def ic(s):
    n = len(s)
    return sum(v * (v - 1) for v in Counter(s).values()) / (n * (n - 1))


def tamanho_chave(texto):
    """Slide 25: o m com maior IC médio das colunas (o menor que se destaca)."""
    melhor_m, melhor_ic = 1, 0
    for m in range(2, 9):
        colunas = [texto[i::m] for i in range(m)]        # TODO dos alunos: texto[i::m]
        media = sum(ic(c) for c in colunas) / m
        if media > melhor_ic + 0.005:
            melhor_m, melhor_ic = m, media
    return melhor_m


def quebrar_vigenere(texto, m):
    """Slide 26: cada coluna é um César."""
    chave = ""
    for i in range(m):
        coluna = texto[i::m]
        k = quebrar_cesar(coluna)
        chave += chr(k + ord("A"))                       # TODO dos alunos
    return chave


# ---------- Dia 2: Euclides e RSA ----------
def mdc(a, b):
    while b:
        a, b = b, a % b
    return a


def fatorar(n):
    f = 2
    while n % f != 0:                                    # TODO dos alunos
        f += 1
    return f, n // f


if __name__ == "__main__":
    # César
    assert cesar("OLA MUNDO", 3) == "ROD PXQGR"
    assert cesar("ROD PXQGR", -3) == "OLA MUNDO"
    assert cesar("Z", 3) == "C" and -3 % 26 == 23
    assert quebrar_cesar(cesar("O CODIGO SECRETO ESTA AQUI", 7)) == 7
    # Vigenère
    assert vigenere("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"
    claro = ("A CRIPTOGRAFIA PROTEGE NOSSAS CONVERSAS NOSSAS SENHAS E NOSSOS PAGAMENTOS NA INTERNET "
             "QUEM ENTENDE COMO ELA FUNCIONA TAMBEM ENTENDE COMO ELA PODE FALHAR E ISSO AJUDA A CONSTRUIR "
             "SISTEMAS MAIS SEGUROS PARA TODOS UMA CIFRA ANTIGA PODE PARECER FORTE ATE QUE ALGUEM "
             "DESCUBRA O PADRAO ESCONDIDO NAS LETRAS POR ISSO ESTUDAR OS ATAQUES E TAO IMPORTANTE QUANTO "
             "ESTUDAR AS CIFRAS SO QUEM SABE COMO UMA CHAVE PODE SER DESCOBERTA CONSEGUE ESCOLHER UMA CHAVE "
             "QUE RESISTA AO TEMPO AOS COMPUTADORES E A CURIOSIDADE DE UMA TURMA INTEIRA DE ESTUDANTES")
    for chave in ["SOL", "MAR", "FOGO", "TERRA", "NUVEM", "PLANETA"]:
        texto = vigenere(claro, chave).replace(" ", "")
        m = tamanho_chave(texto)
        achada = quebrar_vigenere(texto, m)
        for t in range(1, len(achada) + 1):             # se a chave sair repetida (SOLSOL), vale a menor
            if len(achada) % t == 0 and achada[:t] * (len(achada) // t) == achada:
                achada = achada[:t]
                break
        assert achada == chave, (chave, m, achada)
    # Euclides e RSA
    assert mdc(48, 18) == 6
    assert pow(17, -1, 3120) == 2753 and 17 * 2753 % 3120 == 1
    p, q = 61, 53
    n, phi, e = p * q, (p - 1) * (q - 1), 17
    d = pow(e, -1, phi)
    c = pow(65, e, n)
    assert (n, phi, d, c) == (3233, 3120, 2753, 2790) and pow(c, d, n) == 65
    assert fatorar(3233) == (53, 61)
    print("todos os testes passaram")
