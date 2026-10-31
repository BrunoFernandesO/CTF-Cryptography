# CTF architecture

This describes the CTF server as used in class (V4.3, `ctf-server/`). It is a single Flask application with a SQLite database. It was hosted on PythonAnywhere at `brunofernandeso.pythonanywhere.com`, and students opened it on the lab computers.

## Components

```text
 Student page "/"         --JSON-->  app.py  --sqlite3-->  ctf.db
   polls /api/estado every 10 s        |
   polls /api/board every 8 s          |- puzzles.py   puzzle generation and flag comparison
 Projector "/placar"                   |- secret.key   server secret (or the CTF_SECRET variable)
   polls /api/placar every 3 s         '- flask CLI    organizer commands
 Organizer "/organizador"
   polls /api/organizador/estado every 5 s
 "/colab", "/caderno", "/desafio", "/colab-desafio"  -->  302 to the Colab notebooks
```

- `puzzles.py` holds the word lists and keys, generates the three puzzles and compares flags.
- `app.py` holds the routes, the database code, the answer assignment and the organizer commands (`zerar`, `liberar`, `respostas`, `abrir`, `fechar`, `status`, `senha`).
- The browser keeps a Flask session cookie, signed with the server secret and valid for 3 days. It holds `nick_key` and `token` for students, and `admin` for the organizer.

## Data model

| Table | Columns | Purpose |
| --- | --- | --- |
| `players` | `nick_key` (primary key, lower-case nickname), `display`, `token`, `created`, `pin_hash`, `pin_fails`, `pin_lock` | One row per account. `token` must match the session cookie. It is set to `LIVRE` when the organizer frees the nickname. `pin_hash` is a Werkzeug password hash. `pin_fails` and `pin_lock` implement the PIN lockout. |
| `solves` | `nick_key`, `level`, `ts`; primary key (`nick_key`, `level`) | One row per solved level. Points are computed from this table, never stored. |
| `attempts` | `nick_key`, `level`, `ts` | One row per wrong flag. The count and the latest time give the cooldown. |
| `assignments` | `nick_key`, `level`, `attempt`, `flag_key`; primary key (`nick_key`, `level`), `UNIQUE (level, flag_key)` | Which puzzle seed each player got on each level, and its normalized flag. The unique constraint is what guarantees that no two players share an answer. |
| `settings` | `key`, `value` | `open_levels` (for example `1,2`) and `admin_hash` (the organizer password hash). |

Databases from V2 to V4.2 lack the three PIN columns. `init_db()` runs at start-up, adds missing columns with `ALTER TABLE` and keeps every row. Accounts created before V4.3 have no PIN. They can still be used from the browser that created them, which records a PIN on the next login. From any other computer they must be freed by the organizer first.

## Puzzle derivation

Each puzzle comes from a random generator seeded with

```text
HMAC-SHA256(server secret, "nickname:level:attempt")
```

where `nickname` is lower-cased and `attempt` is a small integer. The same inputs always give the same puzzle, so restarting the server does not change anyone's puzzle as long as `secret.key` is kept. Without the secret, nobody can compute another player's puzzle or answer.

| Level | Puzzle | Answer space |
| --- | --- | --- |
| 1 · Caesar · 100 pts | A fixed Portuguese sentence plus the password `TERM-ANIMAL`, shifted by k from 1 to 25 | 40 terms × 40 animals = 1,600 passwords |
| 2 · Vigenère · 200 pts | A fixed 448-letter Portuguese text, encrypted with one key from a list | 131 keys of 3 to 7 letters, each tested against the class attack |
| 3 · RSA · 300 pts | p and q from the 122 primes between 211 and 997, a public exponent e from 17 to 37 coprime with φ(n), a random message m from 1000 to n − 1 | effectively unlimited (the flag is m) |

### Unique answers

The first time a player opens a level, `assignment()` tries `attempt = 0, 1, 2, …` (at most 500). For each one it generates the puzzle, normalizes the flag and tries to insert it into `assignments`. The `UNIQUE (level, flag_key)` constraint rejects a flag that another player already holds, and the loop moves to the next attempt. The chosen attempt is stored, so the player sees the same puzzle afterwards. If the space runs out (more than 131 players on level 2), the player gets attempt 0 and the row is marked as a duplicate, so the server keeps working.

Without this step, answers would collide often. With the secret and nicknames used in `tests/test_ctf.py`, 60 students would hold only 58 distinct level 1 passwords and 50 distinct level 2 keys if each simply got attempt 0.

### Flag comparison

Flags are compared after removing spaces, hyphens and underscores and converting to upper case, so `flag{cifra coruja}` equals `FLAG{CIFRA-CORUJA}`. The comparison uses `hmac.compare_digest`. Flags are never sent to the browser.

## Threat model

The server protects a classroom game, not real data. The threats it answers are the ones expected from a class of about 35 students on shared lab computers.

| Threat | Countermeasure |
| --- | --- |
| **Copying a classmate's answer.** Students sit side by side and can read each other's screens. | Every player has a different puzzle and, through `assignments`, a different answer on each level. A copied flag is simply wrong. |
| **Brute-forcing flags.** Level 1 has 1,600 passwords and level 2 has 131 keys, so a script could try them all. | Escalating cooldowns per player and level, enforced on the server: 3 s after each of the first 5 wrong flags, 30 s after the 6th to 10th, 120 s after that. Trying all 131 keys would take about four hours. Breaking the cipher takes minutes. |
| **Solving at home with online tools before the lesson.** Caesar and Vigenère solvers are one search away. | Levels are closed by default and opened by the organizer during class (`/organizador` or `flask --app app abrir`). A closed level sends neither ciphertext nor hint, and its flags are rejected with 403. The student page notices within 10 s when a level opens. |
| **Losing an account between days on shared lab computers that sit behind one IP address.** The browser that held the session on day 1 may not be the one used on day 2, or the cookie may be gone. | Accounts are nickname + 4-digit PIN, so a student gets back in from any computer. Five wrong PINs in a row lock that nickname, not an IP address, for 5 minutes, because every lab computer shares one address and an IP lock would block the whole room. A student who forgets the PIN is freed by the organizer: the PIN and session are cleared, and points and puzzles are kept. |
| **Guessing the organizer password.** | The password is stored as a hash in `settings`. Five wrong passwords lock that IP address for 5 minutes, and 20 wrong passwords from any address within 5 minutes lock the panel for everyone. Organizer API calls must be JSON requests, which a plain HTML form on another site cannot send. |

Out of scope: the server does not defend against someone who has the server secret or the database file, does not rate-limit page loads, and keeps the organizer lockout counters in memory, so they reset when the server restarts. It is meant to run for the length of an event.

## Operating notes

- Keep `secret.key` and `ctf.db` between the two days. Deleting the secret changes every puzzle; `flask --app app zerar` deletes all players and points.
- `zerar` keeps the organizer password and the open/closed state of the levels.
- `flask --app app respostas NICKNAME` prints a player's puzzle and answer, to help a student who is stuck.
- The tests in `tests/test_ctf.py` cover each guarantee above.
