# Criptografia na Prática

[Português](README.pt-BR.md)

Materials and CTF platform of **"Criptografia na Prática: Matemática e Python do Zero ao RSA"** (Cryptography in Practice: Math and Python from Zero to RSA), a two-day, 8-hour hands-on course taught by Bruno Fernandes Ortega on 26 and 27 October 2026 at WorkInTech 2026 (6th edition). WorkInTech is the tech event organized by Axion, the student tech organization of UniCesumar in Maringá, Brazil.

The course is in Portuguese. So are the slides, notebooks, code comments and the CTF interface.

## Audience and results

- About 35 students, mostly in the first and second year of Software Engineering and of Systems Analysis and Development.
- Every participant solved CTF level 1 (Caesar) and level 2 (Vigenère) with code they wrote in class.
- Euclid's algorithm, RSA and CTF level 3 were prepared but not reached. The hands-on blocks took about 1.6 times the planned time, and depth was chosen over coverage.

## Teaching approach

- **Students write the attacks, not only the ciphers.** After implementing Caesar, they break it by brute force and teach Python to recognize Portuguese. After Vigenère, they find the key length with the index of coincidence and break each column as a Caesar cipher.
- **Skeletons, not finished code.** Code on the slides has `???` where the student writes the missing step, marked with `TODO`. The solutions are in the speaker notes and in `reference/solucoes.py`.
- **Self-checks.** Each exercise in the Colab notebooks is followed by a "Conferir" cell that says whether the function is right. A "Plano B" cell loads the day 1 functions ready-made, so nobody is blocked on day 2.
- **Two notebook levels.** `caderno-aluno.ipynb` follows the slides. `caderno-desafio.ipynb` has larger TODOs for students who want more difficulty.
- **The CTF follows the lessons.** Level 1 comes after Caesar on day 1; levels 2 and 3 after Vigenère and RSA. Students run their own code on a puzzle that only they received.

## How the CTF works

```text
 Students ("/")  --HTTP-->  Flask (app.py)  -->  SQLite (ctf.db)
                             |- puzzles.py: puzzles derived from HMAC(secret, nickname:level:attempt)
                             |- gives each student an answer nobody else has (UNIQUE in the database)
                             '- checks flags only on the server
 Projector ("/placar") <-- /api/placar every 3 s: ranking, first solver per level, latest solves
 "/organizador"  --> password-protected panel to open and close levels during class
 "/colab", "/desafio" --> short links to the two notebooks, typed on the lab computers
```

| Level | Cipher | What the student does | Different answers |
| --- | --- | --- | --- |
| 1 · 100 pts | Caesar, k from 1 to 25 | brute force the 25 keys and read the password | 1,600 (40 terms × 40 animals) |
| 2 · 200 pts | Vigenère, 3- to 7-letter key | index of coincidence to find the key length, then one Caesar per column | 131 keys, all tested against the attack |
| 3 · 300 pts | RSA with p, q between 200 and 1000 | factor n, compute φ(n), d and m | effectively unlimited |

Guarantees:

- **Unique answers.** The first time a student opens a level, the server picks a puzzle whose flag nobody else has and stores the choice. Copying a classmate's flag does not work. On level 2 this holds for up to 131 players.
- **Cooldowns.** Each wrong flag costs a growing wait, per player and per level: 3 s for the first 5 errors, 30 s for the next 5, then 120 s. Trying the whole key list is not practical.
- **Class-time gating.** Each level has a switch and starts closed. A closed level sends neither the ciphertext nor the hint, and the server rejects its flags. Nobody can solve it at home with an online tool before the lesson.
- **Nickname + PIN accounts.** Students choose a 4-digit PIN with their nickname and use it to return to their account on another computer on day 2. Five wrong PINs lock the nickname for 5 minutes. If a student forgets the PIN, the organizer frees the nickname, and the points and puzzles are kept.

The data model, puzzle derivation and threat model are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Run it locally

Python 3.8 or newer.

```bash
cd ctf-server
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app senha              # set the organizer password (8+ characters)
flask --app app abrir todos        # open all levels (they start closed)
python app.py                      # http://localhost:5000, /placar, /organizador
```

The first run creates `secret.key` and `ctf.db` in `ctf-server/`. Both are ignored by git. Keep `secret.key` between the two days of a class: it keeps each student's puzzles the same.

Tests and reference solutions, from the repository root:

```bash
pip install -r ctf-server/requirements.txt pytest
pytest                             # CTF test suite (tests/)
python reference/solucoes.py       # prints "todos os testes passaram"
```

## Repository layout

```text
ctf-server/          CTF server as used in class (V4.3): Flask app, puzzles, templates, static files
notebooks/           Colab notebooks: caderno-aluno (student) and caderno-desafio (challenge)
reference/           solucoes.py: the slide code with every TODO filled in, with asserts
slides/
  criptografia-na-pratica-oficina.pptx   the 37-slide PowerPoint deck taught in class
  conteudo-37-slides.md                  text and speaker notes of that deck
  prototype-html/                        first 34-slide HTML prototype (18 Oct)
tests/               pytest suite for the CTF; legacy/ holds the original validation scripts
docs/                TIMELINE.md, ARCHITECTURE.md, CURRICULUM.md
```

## Timeline

Everything was built between 14 and 26 October 2026. The repository was created afterwards. Each commit carries the date its content existed. Times are UTC−3. "approx." marks a time inferred from the order of events. Details are in [docs/TIMELINE.md](docs/TIMELINE.md).

| Date | Snapshot | Fidelity |
| --- | --- | --- |
| 14 Oct 22:08 | CTF puzzle generator and attack validation | exact |
| 14 Oct 22:10 | CTF V1: server, student page, projector scoreboard | exact |
| 14 Oct 22:12 | Slide overflow checker | exact |
| 18 Oct 10:28 | HTML prototype deck, 34 slides | exact |
| 18 Oct 10:33 | Reference solutions | exact |
| 21 Oct 20:06 | CTF V2: unique answers, escalating cooldowns, new visual | exact |
| 21 Oct 21:50 | Student notebook | exact (outputs removed) |
| 21 Oct 23:23 | Student notebook renumbered for the 37-slide deck | exact (outputs removed) |
| 21 Oct 23:51 | CTF V3: /colab short link | exact |
| 25 Oct 11:00 approx. | CTF V4: levels open only during class, organizer panel | reconstructed |
| 25 Oct 16:53 | Challenge notebook | exact (outputs removed) |
| 25 Oct 16:59 | CTF V4.2: /desafio short link | exact |
| 25 Oct 17:33 | CTF V4.3: nickname + PIN accounts | exact |
| 25 Oct 19:30 approx. | Text and speaker notes of the 37-slide deck | exact |
| 26 Oct 16:36 | Final PowerPoint deck | exact, with a sensitivity label and contact details removed |

## Credits

- Axion and the WorkInTech 2026 organizers, for the event and the visual identity used in the slides and the CTF.
- The students, who wrote the attacks.

## License

- Code (`ctf-server/`, `reference/`, `tests/`): MIT License, see [LICENSE](LICENSE).
- Teaching materials (`slides/`, `notebooks/`, `docs/`, the README files): Creative Commons Attribution 4.0 International, see [LICENSE-CC-BY-4.0.txt](LICENSE-CC-BY-4.0.txt).
- Not covered by either license: the Axion and WorkInTech logos and the background image (`ctf-server/static/axion-logo.svg`, `wit-mark.png`, `fundo.jpg`, and the same images in the slides) belong to Axion and are published with its permission. Historical photographs and third-party diagrams in the slides keep their own terms. Fonts embedded in the PowerPoint file keep their own licenses, listed in the file's properties.
