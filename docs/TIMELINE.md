# Timeline

The workshop materials and the CTF were built between 14 and 26 October 2026 and kept as files. There was no git repository at the time. The repository was created on 29–31 October 2026 from the files that survived. Each snapshot became one commit, dated when its content existed.

Rules followed:

- A commit's date is the moment its content existed, not when the work on it started. Author date and committer date are equal.
- Times are America/Sao_Paulo (UTC−3). Timestamps inside zip files are local time.
- **exact** means the commit contains the original files. **reconstructed** means the original files were not preserved and the content was rebuilt from the nearest exact versions, as described below.
- **approx.** marks a time inferred from the order of events, not read from a file.
- Each commit message ends with a `Source:` line naming its input.

## Snapshots

| Commit | Date and time (UTC−3) | Content | Fidelity | Source |
| --- | --- | --- | --- | --- |
| `b596096` | 2026-10-14 22:08:42 | CTF puzzle generator (V1) and the attack validation script | exact | backup zip of 18 Oct |
| `595471b` | 2026-10-14 22:10:40 | CTF V1: Flask server, student page, projector scoreboard, reference attacks, UI test | exact | backup zip |
| `a0dd6aa` | 2026-10-14 22:12:10 | Slide overflow checker | exact | backup zip |
| `be54622` | 2026-10-18 10:28:00 | HTML source of the 34-slide prototype deck | exact | backup zip (state of 18 Oct 10:28) |
| `345597e` | 2026-10-18 10:33:41 | Reference solutions with asserts | exact | project file `03-codigo-python.py` |
| `5dff532` | 2026-10-21 20:06:36 | CTF V2: unique answer per student, escalating cooldowns, Axion visual, PythonAnywhere | exact | `ctf-server-v2.zip` |
| `ea2c05a` | 2026-10-21 21:50:14 | Student Colab notebook, first numbering | exact, outputs removed | notebook downloaded from Google Drive |
| `db63ca6` | 2026-10-21 23:23:45 | Student notebook renumbered for the 37-slide deck | exact, outputs removed | notebook downloaded from Google Drive |
| `a4e2020` | 2026-10-21 23:51:00 | CTF V3: `/colab` and `/caderno` short links | exact | `ctf-server-v3.zip` |
| `d61778d` | 2026-10-25 11:00 approx. | CTF V4: levels open only during class, organizer panel | **reconstructed** | built from the exact V4.2, see below |
| `febba5d` | 2026-10-25 16:53:01 | Challenge notebook with larger TODOs | exact, outputs removed | notebook downloaded from Google Drive |
| `3c89768` | 2026-10-25 16:59:24 | CTF V4.2: `/desafio` short link to the challenge notebook | exact | `ctf-server-v4.2.zip` |
| `be09ee8` | 2026-10-25 17:33:38 | CTF V4.3: nickname + PIN accounts, `liberar` keeps points, database migration | exact | `ctf-server-v4.3.zip` |
| `ba7f193` | 2026-10-25 19:30 approx. | Text and speaker notes of the 37-slide deck | exact | project file `02-slides-conteudo.md` |
| `17bf4a2` | 2026-10-26 16:36:00 | Final PowerPoint deck, as last edited on the first day of class | exact, with two changes (see below) | `Criptografia na Pratica - oficina.pptx` |

Work done when the repository was created carries its real date (31 October 2026): the pytest suite and the move of `testes/` to `tests/legacy/`, the README files, this timeline, `ARCHITECTURE.md`, `CURRICULUM.md` and the license files.

## Notes on individual snapshots

**Times taken from the zips.** The plan for this repository had approximate times for V2 (19:30), V3 (23:45), V4.2 (17:05) and V4.3 (17:40). The original zips of those versions were found, and each commit uses the newest file timestamp inside its zip instead. The order of events did not change: V2 comes before the first notebook, V3 after the renumbered notebook, and V4.2 six minutes after the challenge notebook it links to.

**V4 is reconstructed.** The V4 zip was not preserved. V4 was rebuilt from the exact V4.2 files by removing only what V4.2 added: the `DESAFIO_URL` constant, the `/desafio` and `/colab-desafio` routes, the V4.2 line in the module docstring and comment, and the V4.2 lines in the README. The V4.2 README states that the rest of the server is identical to V4. Everything else in the V4 commit, including the templates, the organizer panel and the static files, is byte for byte V4.2. Before committing, the rebuilt V4 was checked: it imports, every route it has answers, `/desafio` returns 404, closed levels hide their data and reject flags with 403, and a test student solves levels 1–3 with `reference/solucoes.py`.

**V4.3 in two sources.** The same V4.3 source exists in the project file `04-ctf-servidor.md` and in `ctf-server-v4.3.zip`. They are identical except for line endings. The commit uses the zip.

**V2 drops `referencia/`.** V1 shipped the complete attacks in `ctf-server/referencia/ataques.py`. V2 removed that folder, so the V2 commit deletes it. The same code, with asserts, is in `reference/solucoes.py`.

**Test script paths.** The two scripts in `testes/` (`attack_test.py`, `ui_test.py`) originally began with a `sys.path` line, and saved screenshots to paths, inside a temporary folder of the machine where they were written. In this history those paths read `../ctf-server` and `out/`, and the commits that introduced the scripts say so. Nothing else in the scripts differs from the originals.

**Notebooks.** The three notebooks were downloaded from Google Drive and passed through a script that removes cell outputs and Colab runner metadata (which hold the runner's Google account name and id). Cell sources are unchanged.

**Final deck.** The PowerPoint file was last edited on 26 October, the first day of class, with small changes after it became clear there would be no time for RSA on day 2. Two things were changed for the public copy and nothing else. First, a Microsoft 365 sensitivity label ("Interno"), added by the account the file happened to be saved with, was removed together with the "CLASSIFICAÇÃO: INTERNO" footer it put on the slide master. Second, the personal contact details on slide 37 were replaced with the placeholders `[seu LinkedIn]`, `[seu Instagram]` and `[seu e-mail]`, and the contact QR code with a plain box.

**Not published.** The answer-key notebook, the server's `secret.key` and `ctf.db`, and any per-student data (nicknames, scores) are not in any commit. Results appear only as aggregate figures in the README.
