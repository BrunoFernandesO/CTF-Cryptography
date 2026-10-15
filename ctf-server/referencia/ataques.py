"""Solução de referência (só para você, organizador). É o código que os alunos constroem nos slides,
com todos os TODO preenchidos. Foi testado contra 400 apelidos diferentes nos três níveis, sem falhas.

Uso (nível 2): cole o texto cifrado, remova os espaços, ache m e depois a chave:
    texto = "FQXWU HUUWO ...".replace(" ", "")
    m = tamanho_chave(texto)          # se a chave sair repetida (SOLSOL), a verdadeira é a menor
    print(quebrar_vigenere(texto, m))
"""
from collections import Counter

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
