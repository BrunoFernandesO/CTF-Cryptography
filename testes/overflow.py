import json, re
from playwright.sync_api import sync_playwright
D = "deck/project/"
order = json.load(open(D + "deck.json"))["order"]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    bad = []
    for sid in order:
        s = open(D + f"slides/{sid}.html", encoding="utf-8").read()
        s = re.sub(r"<aside>.*?</aside>", "", s, flags=re.S)
        s = s.replace("<section ", '<section data-x="1" ', 1)
        page = ('<!doctype html><html><head><meta charset="utf-8"><style>*{box-sizing:border-box;margin:0;padding:0}'
                'ul,ol{padding-left:48px}table{border-collapse:collapse}td,th{padding:12px 16px}'
                'section{position:relative;width:1920px;height:1080px;overflow:hidden}</style></head><body>' + s + '</body></html>')
        pg.set_content(page)
        res = pg.evaluate("""() => {
          const sec = document.querySelector('section'); const top = sec.getBoundingClientRect().top;
          let maxBottom = 0, maxRight = 0;
          sec.querySelectorAll('*').forEach(el => {
            const cs = getComputedStyle(el); if (cs.position === 'absolute' && el.textContent.includes('WorkInTech')) return;
            if (cs.position === 'absolute' && /^\\d{2}$/.test(el.textContent.trim())) return;
            const r = el.getBoundingClientRect(); if (r.width === 0) return;
            maxBottom = Math.max(maxBottom, r.bottom - top); maxRight = Math.max(maxRight, r.right);
          });
          return {maxBottom: Math.round(maxBottom), maxRight: Math.round(maxRight)};
        }""")
        flag = "  <-- ESTOURA" if res["maxBottom"] > 925 or res["maxRight"] > 1800 else ""
        if flag: bad.append(sid)
        print(f"{sid:18} bottom={res['maxBottom']:5} right={res['maxRight']:5}{flag}")
    b.close()
print("problemas:", bad)
