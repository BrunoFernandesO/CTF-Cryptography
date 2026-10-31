# Legacy validation scripts

The scripts used on 14 Oct to check the first version of the CTF and the HTML deck. They are kept as they were, except that the hardcoded paths now point into this repository. They are plain scripts, not pytest tests; the current test suite is in `tests/`.

| Script | What it checked | Notes |
| --- | --- | --- |
| `attack_test.py` | The slide attacks (Caesar brute force, Vigenère key length and columns, factoring a small RSA modulus) solve the generated puzzles for 400 nicknames. | Written for CTF V1: it imports `check_flag`, which V2 replaced. It runs only with V1's `ctf-server/puzzles.py` (commit 595471b) on its path. |
| `ui_test.py` | The student page logs in, shows three levels, accepts a flag and updates the scoreboard. | Needs Playwright and a server on port 5055. Screenshots go to `tests/legacy/out/`. Written for V1's login, which had no PIN. |
| `overflow.py` | No slide of the HTML prototype deck overflows the 1920×1080 frame. | Needs Playwright. Reads `slides/prototype-html/`. |

The scripts launch Chromium from `/opt/pw-browsers/chromium`, the path in the environment where they were written. Change `executable_path` or remove it to use Playwright's own browser.
