import json, time
from playwright.sync_api import sync_playwright

URL   = "http://localhost:4001/preview/prompt-test3.html"
MODELS = [
    ("GPT-2 Q3_K_M",   "gpt2-Q3_K_M|tensorblock/gpt2-GGUF|completion"),
    ("SmolLM2 Q3_K_L", "SmolLM2-135M-Instruct-Q3_K_L|lmstudio-community/SmolLM2-135M-Instruct-GGUF|instruct"),
]

def run(page, label, val):
    print(f"\n{'='*58}\n  {label}\n{'='*58}")
    page.reload(); page.wait_for_load_state("networkidle")
    page.select_option("#msel", val)
    page.click("#rb")
    last=""; deadline=time.time()+10*60
    while time.time()<deadline:
        s=page.inner_text("#status")
        if s!=last: print(f"  [{time.strftime('%H:%M:%S')}] {s}"); last=s
        if s.startswith("Done") or page.is_enabled("#cb"): break
        time.sleep(3)
    rows=page.evaluate("""()=>{
      const r=[];
      document.querySelectorAll('#tb tr:not(.sr)').forEach(tr=>{
        const c=tr.querySelectorAll('td');
        if(c.length<5) return;
        r.push({idx:c[0].innerText.trim(),label:c[1].innerText.trim(),
                raw:c[2].innerText.trim(),pass:c[3].innerText.trim()==='✓',reason:c[4].innerText.trim()});
      });
      return r;
    }""")
    print(f"\n  {'#':<4}{'PASS':<5}{'RAW':<38}REASON")
    print(f"  {'-'*4}{'-'*5}{'-'*38}{'-'*18}")
    for r in rows:
        raw=r['raw'][:36].replace('\n','↵')
        print(f"  {r['idx']:<4}{'✓' if r['pass'] else '✗':<5}{raw:<38}{r['reason']}")
    good=[r['raw'] for r in rows if r['pass']]
    print(f"\n  {len(good)}/{len(rows)} passed: {good}")
    return rows

def main():
    all_r={}
    with sync_playwright() as pw:
        br=pw.chromium.launch(headless=True,args=["--no-sandbox","--disable-setuid-sandbox","--enable-features=SharedArrayBuffer"])
        ctx=br.new_context(extra_http_headers={"Cross-Origin-Embedder-Policy":"require-corp","Cross-Origin-Opener-Policy":"same-origin"})
        pg=ctx.new_page(); pg.set_default_timeout(10*60*1000)
        pg.on("pageerror",lambda e: print(f"  ERR:{e}"))
        pg.goto(URL,wait_until="networkidle")
        for label,val in MODELS:
            all_r[label]=run(pg,label,val)
        br.close()

    print(f"\n\n{'='*58}\n  FINAL SUMMARY\n{'='*58}")
    for label,rows in all_r.items():
        good=[r['raw'] for r in rows if r['pass']]
        unique=list(dict.fromkeys(good))
        print(f"\n  {label}: {len(good)}/{len(rows)} passed, {len(unique)} unique")
        for n in unique: print(f"    • {n}  (×{good.count(n)})")

    with open("test_results3.json","w") as f: json.dump(all_r,f,indent=2)
    print("\nSaved test_results3.json")

if __name__=="__main__": main()
