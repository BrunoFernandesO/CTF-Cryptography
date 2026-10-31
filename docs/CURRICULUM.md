# Curriculum

The two-day plan of "Criptografia na Prática: Matemática e Python do Zero ao RSA", as prepared in the 37-slide deck ([slides/conteudo-37-slides.md](../slides/conteudo-37-slides.md)). Each day was planned as 3 h 30 min with one break. The planned minutes come from the speaker notes of slide 4.

Students worked on the lab computers in Google Colab (`notebooks/caderno-aluno.ipynb`, or `caderno-desafio.ipynb` for larger TODOs). Code on the slides has `???` where the student writes the missing step. The solutions are in the speaker notes and in `reference/solucoes.py`.

## What was taught and what was prepared

- **Taught:** the opening, history, types, Caesar and Vigenère blocks, up to breaking Vigenère in Python (slides 1–29). Every participant solved CTF level 1 (Caesar) and level 2 (Vigenère) with their own code.
- **Prepared, not reached:** Euclid and the modular inverse, RSA (slides 30–34) and CTF level 3.
- **Why:** the hands-on blocks took about 1.6 times the planned time, and depth was chosen over coverage: the class finished the Caesar and Vigenère attacks instead of rushing through RSA.

The RSA material is complete in the slides, the notebooks, `reference/solucoes.py` and the CTF, so it can be used in a longer edition of the course.

## Day 1 · 26 October · From the note to Vigenère

| Block | Minutes | Slides | Content | Hands-on |
| --- | --- | --- | --- | --- |
| Opening | 10 | 1–4 | `ROD PXQGR` projected on the cover as a puzzle (Caesar, k = 3). Class agreements, the speaker, the two-day plan. | Try to read the cover. |
| Introduction and history | 25 | 5–11 | Etymology (kryptós + gráphein). The note passed through the classroom as an analogy for data on the internet. Antiquity (Egypt, the scytale, Caesar), Al-Kindi's frequency analysis, Vigenère and its break by Babbage and Kasiski, Enigma, Diffie–Hellman and RSA (1976–77), AES. Confidentiality, integrity and authenticity in everyday use. | |
| Types of cryptography | 10 | 12–13 | Symmetric, asymmetric and hash functions; where Caesar, Vigenère and RSA fit. Kerckhoffs's principle: the security must be in the key, so breaking public algorithms is a valid way to study them. | |
| Caesar with Python, CTF level 1, automating the attack | 85 | 14–20 | Letters as numbers, C = (P + k) mod 26, modular arithmetic with the clock. Opening the notebook through the `/colab` short link. Python for students coming from C or Java (`ord`, `chr`, `%` with negative numbers). | Write `cesar()`. Break it by brute force over the 25 keys. Solve CTF level 1. Write `pontuacao()` so `quebrar_cesar()` finds k by counting A, E and O. |
| Break | 15 | | | |
| Vigenère | 55 | 21–24 | Cᵢ = (Pᵢ + K[i mod m]) mod 26: a Caesar whose shift changes with each letter. How to break it, as an idea only: find the key length, then each column is a Caesar. End of day 1. | Write `vigenere()` by reusing `cesar()`. If time is short, the function is given ready-made. |

## Day 2 · 27 October · Breaking things, and RSA

| Block | Minutes | Slides | Content | Hands-on |
| --- | --- | --- | --- | --- |
| Warm-up and breaking Vigenère | 49 | 25–29 | Three questions from day 1. Index of coincidence: the chance that two letters drawn from the text are equal (about 0.08 in Portuguese, 0.04 in random text). A Caesar shift does not change it, so the right key length m gives columns with the Portuguese value. | A "Plano B" cell loads the day 1 functions. Split the text into m columns and find m with `tamanho_chave()`. Recover the key column by column with `quebrar_cesar()`. Solve CTF level 2. |
| Euclid | 25 | 30 | gcd by Euclid's algorithm, modular inverse with `pow(a, -1, n)`, without the proof of Euler's theorem. | Write `mdc()`. |
| Break | 15 | | | |
| RSA | 75 | 31–34 | Public padlock, private key. Key generation by hand with p = 61, q = 53, e = 17, d = 2753. RSA in a few lines of Python. Breaking a small RSA by factoring n. | Write `fatorar()` and recover φ(n), d and m. |
| Final CTF | 25 | 35 | All three levels, each student with their own puzzle. | Solve levels 1–3. |
| Real-world RSA and closing | 20 | 36–37 | Use established libraries in real systems; implementing your own is for learning. Questions, and further study: CryptoHack, Dan Boneh's Cryptography I, Cryptopals. | |

Planned total: 200 of 210 minutes on day 1 and 209 of 210 on day 2. The speaker notes give fallbacks if time runs short: hand out `vigenere()` ready-made on day 1, and on day 2 give the index of coincidence loop ready-made and show the RSA attack as a demonstration. On the day, the blocks before RSA took the time instead.

## CTF levels and where they fit

| Level | After | Uses |
| --- | --- | --- |
| 1 · Caesar | slides 19–20, day 1 | `cesar()`, brute force over the 25 keys, reading the password |
| 2 · Vigenère | slides 28–29, day 2 | `ic()`, `tamanho_chave()`, `quebrar_vigenere()` |
| 3 · RSA | slide 34, day 2 | `fatorar()`, `pow(e, -1, phi)`, `pow(c, d, n)` |

The organizer opens each level from `/organizador` when the class reaches it; until then the level shows no data (see [ARCHITECTURE.md](ARCHITECTURE.md)).
