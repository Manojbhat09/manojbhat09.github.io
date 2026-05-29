"""Compare SmolLM2 quantizations: Q2_K, Q3_K_S, IQ3_XS, Q3_K_M vs lmstudio Q3_K_L baseline."""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:4001/preview/smollm-compare.html"

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=[
            "--no-sandbox","--disable-setuid-sandbox","--enable-features=SharedArrayBuffer"
        ])
        ctx = browser.new_context(extra_http_headers={
            "Cross-Origin-Embedder-Policy":"require-corp",
            "Cross-Origin-Opener-Policy":"same-origin",
        })
        page = ctx.new_page()
        page.set_default_timeout(20 * 60 * 1000)
        page.on("pageerror", lambda e: print(f"  PAGE ERR: {e}"))
        page.goto(URL, wait_until="networkidle")

        print("Starting comparison run (5 models × 5 prompts)…")
        page.click("#rb")

        # Stream status while waiting
        last = ""; deadline = time.time() + 18 * 60
        while time.time() < deadline:
            s = page.inner_text("#status")
            if s != last:
                print(f"  [{time.strftime('%H:%M:%S')}] {s}")
                last = s
            if s == "Done" or page.is_enabled("#cb"):
                break
            time.sleep(4)

        # Scrape results table
        rows = page.evaluate("""() => {
            const r = [];
            document.querySelectorAll('#tb tr:not(.sr)').forEach(tr => {
                const c = tr.querySelectorAll('td');
                if (c.length < 7) return;
                r.push({
                    idx:    c[0].innerText.trim(),
                    model:  c[1].innerText.trim(),
                    size:   c[2].innerText.trim(),
                    seed:   c[3].innerText.trim(),
                    raw:    c[4].innerText.trim(),
                    pass:   c[5].innerText.trim() === '✓',
                    reason: c[6].innerText.trim(),
                });
            });
            return r;
        }""")

        browser.close()

    # Group by model
    from collections import defaultdict
    by_model = defaultdict(list)
    for r in rows:
        by_model[r['model']].append(r)

    print(f"\n{'='*65}")
    print(f"  {'MODEL':<35} {'SIZE':<10} {'PASS':<8} NAMES")
    print(f"  {'-'*35} {'-'*10} {'-'*8} {'-'*20}")
    for model, results in by_model.items():
        passed = [r for r in results if r['pass']]
        names  = [r['raw'] for r in passed]
        size   = results[0]['size'] if results else '?'
        mark   = '★' if 'baseline' in model else ' '
        print(f"  {mark} {model:<34} {size:<10} {len(passed)}/{len(results)}     {names}")

    print(f"\n{'='*65}\n  DETAIL\n{'='*65}")
    for model, results in by_model.items():
        print(f"\n  {model}")
        for r in results:
            mark = '✓' if r['pass'] else '✗'
            print(f"    {mark}  seed='{r['seed']}'  →  '{r['raw']}'  {r['reason']}")

    with open("smollm_compare.json", "w") as f:
        json.dump({"rows": rows, "by_model": {k:v for k,v in by_model.items()}}, f, indent=2)
    print("\nSaved smollm_compare.json")

if __name__ == "__main__":
    main()
