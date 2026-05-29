"""Round 2 headless test — ML-jargon seeds for GPT-2, quoted-only for SmolLM2."""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:4001/preview/prompt-test2.html"
MODELS = [
    ("GPT-2 Q3_K_M",   "gpt2-Q3_K_M|tensorblock/gpt2-GGUF|completion"),
    ("SmolLM2 Q3_K_L", "SmolLM2-135M-Instruct-Q3_K_L|lmstudio-community/SmolLM2-135M-Instruct-GGUF|instruct"),
]

def run_model(page, label, sel_value):
    print(f"\n{'='*60}\n  {label}\n{'='*60}")
    page.reload()
    page.wait_for_load_state("networkidle")
    page.select_option("#model-sel", sel_value)
    page.click("#run-btn")

    last = ""
    deadline = time.time() + 10 * 60
    while time.time() < deadline:
        status = page.inner_text("#status")
        if status != last:
            print(f"  [{time.strftime('%H:%M:%S')}] {status}")
            last = status
        if status.startswith("Done") or page.is_enabled("#copy-btn"):
            break
        time.sleep(3)

    rows = page.evaluate("""() => {
        const r = [];
        document.querySelectorAll('#tbody tr:not(.section-row)').forEach(tr => {
            const c = tr.querySelectorAll('td');
            if (c.length < 5) return;
            r.push({ idx:c[0].innerText.trim(), label:c[1].innerText.trim(),
                      raw:c[2].innerText.trim(), pass:c[3].innerText.trim()==='✓', reason:c[4].innerText.trim() });
        });
        return r;
    }""")

    print(f"\n  {'#':<4} {'PASS':<5} {'RAW':<38} REASON")
    print(f"  {'-'*4} {'-'*5} {'-'*38} {'-'*20}")
    for r in rows:
        raw = r['raw'][:36].replace('\n','↵')
        print(f"  {r['idx']:<4} {'✓' if r['pass'] else '✗':<5} {raw:<38} {r['reason']}")
    good = [r['raw'] for r in rows if r['pass']]
    print(f"\n  {len(good)}/{len(rows)} passed")
    print(f"  Passed: {good}")
    return rows

def main():
    all_results = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-setuid-sandbox","--enable-features=SharedArrayBuffer"])
        ctx = browser.new_context(extra_http_headers={"Cross-Origin-Embedder-Policy":"require-corp","Cross-Origin-Opener-Policy":"same-origin"})
        page = ctx.new_page()
        page.set_default_timeout(10 * 60 * 1000)
        page.on("pageerror", lambda e: print(f"  ERR: {e}"))
        page.goto(URL, wait_until="networkidle")

        for label, val in MODELS:
            all_results[label] = run_model(page, label, val)
        browser.close()

    print(f"\n\n{'='*60}\n  SUMMARY\n{'='*60}")
    for label, rows in all_results.items():
        good = [r['raw'] for r in rows if r['pass']]
        print(f"\n  {label} — {len(good)}/{len(rows)} passed:")
        for n in good: print(f"    • {n}")

    with open("test_results2.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nSaved test_results2.json")

if __name__ == "__main__":
    main()
