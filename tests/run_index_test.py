"""Validate preview/index.html: LM loads, names added, button works."""
import time, json
from playwright.sync_api import sync_playwright

URL = "http://localhost:4001/preview/index.html"

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
        page.set_default_timeout(10 * 60 * 1000)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL, wait_until="networkidle")

        print("Page loaded. Checking initial state…")

        # Check static names rendered
        titles = page.query_selector_all('.hero-title')
        print(f"  Initial pool size: {len(titles)} titles")

        # Check button is visible
        btn_visible = page.is_visible('#lm-ctrl')
        print(f"  Floating button visible: {btn_visible}")

        ctrl_text = page.inner_text('#lm-ctrl-text')
        print(f"  Button text: '{ctrl_text}'")

        # Wait for LM to load and generate names (up to 8 min)
        print("\nWaiting for LM to generate names…")
        last = ""; deadline = time.time() + 8 * 60
        while time.time() < deadline:
            t = page.inner_text('#lm-ctrl-text')
            if t != last:
                print(f"  [{time.strftime('%H:%M:%S')}] ctrl: {t}")
                last = t
            if 'live' in t.lower() or 'failed' in t.lower():
                break
            time.sleep(4)

        # Check pool expanded
        titles_after = page.query_selector_all('.hero-title')
        lm_sparks = page.query_selector_all('.lm-spark')
        print(f"\n  Pool after LM: {len(titles_after)} titles ({len(lm_sparks)} LM-generated)")

        # Read generated names
        names = page.evaluate("""() => {
            const r = [];
            document.querySelectorAll('.hero-title').forEach(el => {
                const spark = el.querySelector('.lm-spark');
                r.push({ text: el.innerText.replace('✦','').trim(), lm: !!spark });
            });
            return r;
        }""")
        print("\n  Full pool:")
        for n in names:
            mark = '✦' if n['lm'] else ' '
            print(f"    {mark} {n['text']}")

        # Test disable button
        print("\nTesting disable button…")
        page.click('#lm-ctrl')
        time.sleep(1)
        btn_after = page.inner_text('#lm-ctrl-text')
        ls_val = page.evaluate("() => localStorage.getItem('wllama_disabled')")
        print(f"  Button after click: '{btn_after}'")
        print(f"  localStorage wllama_disabled: {ls_val}")

        # Test re-enable (just check flag cleared)
        page.click('#lm-ctrl')  # should reload — but we won't wait; just check flag
        time.sleep(1)
        ls_after = page.evaluate("() => localStorage.getItem('wllama_disabled')")
        print(f"  localStorage after re-enable click: {ls_after}")

        print(f"\n  JS errors: {errors if errors else 'none'}")

        browser.close()

    print("\nDone.")

if __name__ == "__main__":
    main()
