import sys
sys.path.insert(0, "../ctf-server")
import puzzles
from playwright.sync_api import sync_playwright
flag = puzzles.make_puzzle(b"ui-secret", "bruno", 1)["flag"]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1200, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://127.0.0.1:5055/")
    pg.fill("#nick", "Bruno"); pg.click("#login-form button")
    pg.wait_for_selector("#levels section")
    assert pg.locator("#levels section").count() == 3
    pg.fill("#levels section:nth-child(1) input", flag)
    pg.click("#levels section:nth-child(1) form button")
    pg.wait_for_selector("#levels section:nth-child(1) .tag.done")
    assert "100 pts" in pg.inner_text("#chip-points")
    pg.wait_for_timeout(500)
    assert "Bruno" in pg.inner_text("#board")
    pg.screenshot(path="out/ui.png", full_page=True)
    pg.goto("http://127.0.0.1:5055/placar"); pg.wait_for_timeout(800)
    assert "Bruno" in pg.inner_text("#board")
    pg.screenshot(path="out/placar.png")
    b.close()
print("UI ok; erros JS:", errs)
