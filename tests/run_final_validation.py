"""Final validation: run production wllama-test.html with both recommended models."""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:4001/preview/wllama-test.html"

MODELS = [
    ("GPT-2 Q3_K_M ★",   "0"),   # index 0 = first option (Q3_K_M recommended)
    ("SmolLM2 Q3_K_L ★",  str),   # find by file name
]

def wait_done(page, timeout=600):
    last=""; deadline=time.time()+timeout
    while time.time()<deadline:
        s=page.inner_text("#s-text")
        if s!=last: print(f"  [{time.strftime('%H:%M:%S')}] {s}"); last=s
        if "ready" in s.lower() or "failed" in s.lower(): break
        time.sleep(3)
    return last

def run_names(page, label, model_idx):
    print(f"\n{'='*58}\n  {label}\n{'='*58}")
    page.reload(); page.wait_for_load_state("networkidle")

    # Select model by option index
    page.evaluate(f"document.getElementById('model-select').selectedIndex = {model_idx}")
    page.dispatch_event("#model-select", "change")
    time.sleep(0.5)

    page.click("#btn-load")
    wait_done(page, timeout=300)

    # Switch to names tab and wait for pane to be visible
    page.click('.tab[data-pane="names"]')
    page.wait_for_selector('#pane-names.active', timeout=5000)
    time.sleep(0.3)

    # Generate names (button is inside the now-visible pane)
    page.wait_for_selector('#btn-gen-names:not([disabled])', timeout=10000)
    page.click("#btn-gen-names")

    # Wait for button re-enabled
    deadline=time.time()+120; last=""
    while time.time()<deadline:
        try:
            enabled=page.is_enabled("#btn-gen-names")
            s=page.inner_text("#s-text")
            if s!=last: print(f"  [{time.strftime('%H:%M:%S')}] gen: {s}"); last=s
            if enabled: break
        except: pass
        time.sleep(3)

    # Scrape chips
    chips = page.evaluate("""() => {
        const r=[];
        document.querySelectorAll('.chip.generated').forEach(c => {
            r.push(c.innerText.replace(/[●·•]/g,'').trim());
        });
        return r;
    }""")

    # Scrape log
    logs = page.evaluate("""() => {
        const r=[];
        document.querySelectorAll('#log-inner .log-line').forEach(l=>{
            const m=l.querySelector('.msg');
            if(m) r.push(m.innerText);
        });
        return r.slice(-20);
    }""")

    print(f"\n  Generated chips: {chips}")
    print(f"\n  Last 20 log lines:")
    for l in logs: print(f"    {l}")
    return chips

def main():
    results = {}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox","--disable-setuid-sandbox","--enable-features=SharedArrayBuffer"])
        ctx=browser.new_context(extra_http_headers={"Cross-Origin-Embedder-Policy":"require-corp","Cross-Origin-Opener-Policy":"same-origin"})
        page=ctx.new_page(); page.set_default_timeout(10*60*1000)
        page.on("pageerror",lambda e: print(f"  PAGE ERR: {e}"))
        page.goto(URL, wait_until="networkidle")

        # SmolLM2 Q3_K_L — look up by file name in the MODELS JS array
        idx = page.evaluate("""() => {
            const opts = document.querySelectorAll('#model-select option');
            for (let o of opts) {
                const modelIdx = parseInt(o.value);
                if (!isNaN(modelIdx) && MODELS[modelIdx] &&
                    MODELS[modelIdx].file === 'SmolLM2-135M-Instruct-Q3_K_L.gguf') {
                    return parseInt(o.value);
                }
            }
            return -1;
        }""")
        print(f"\n  SmolLM2 Q3_K_L is at select index {idx}")
        if idx >= 0:
            results["SmolLM2 Q3_K_L"] = run_names(page, "SmolLM2 Q3_K_L ★", idx)

        browser.close()

    print(f"\n\n{'='*58}\n  FINAL RESULTS\n{'='*58}")
    for label, chips in results.items():
        print(f"\n  {label}: {len(chips)} names generated")
        for c in chips: print(f"    • {c}")

    with open("final_validation.json","w") as f: json.dump(results,f,indent=2)
    print("\nSaved final_validation.json")

if __name__=="__main__": main()
