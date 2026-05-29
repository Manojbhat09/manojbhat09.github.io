"""
Headless Playwright test runner for wllama prompt-test.html
Loads GPT-2 Q3_K_M then SmolLM2 Q3_K_L, runs all test cases, prints a report.
"""
import json, time, sys
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

URL = "http://localhost:4001/preview/prompt-test.html"
# Allow up to 8 min per model (download + all inference)
MODEL_TIMEOUT_MS = 8 * 60 * 1000
# Per-test polling timeout
DONE_POLL_MS     = 7 * 60 * 1000

MODELS = [
    ("GPT-2 Q3_K_M",   "gpt2-Q3_K_M|tensorblock/gpt2-GGUF|completion"),
    ("SmolLM2 Q3_K_L", "SmolLM2-135M-Instruct-Q3_K_L|lmstudio-community/SmolLM2-135M-Instruct-GGUF|instruct"),
]

def run_model(page, label, sel_value):
    print(f"\n{'='*60}")
    print(f"  MODEL: {label}")
    print(f"{'='*60}")

    page.reload()
    page.wait_for_load_state("networkidle")

    # Select model
    page.select_option("#model-sel", sel_value)

    # Click run
    page.click("#run-btn")

    # Stream status updates while waiting
    deadline = time.time() + DONE_POLL_MS / 1000
    last_status = ""
    while time.time() < deadline:
        status = page.inner_text("#status")
        if status != last_status:
            print(f"  [{time.strftime('%H:%M:%S')}] {status}")
            last_status = status
        if status.startswith("Done"):
            break
        # Check if copy button is enabled (signals completion)
        try:
            enabled = page.is_enabled("#copy-btn")
            if enabled:
                break
        except Exception:
            pass
        time.sleep(3)
    else:
        print("  TIMEOUT waiting for tests to complete")
        return []

    # Extract results via JS
    results = page.evaluate("""() => {
        const rows = [];
        document.querySelectorAll('#tbody tr:not(.section-row)').forEach(tr => {
            const cells = tr.querySelectorAll('td');
            if (cells.length < 6) return;
            rows.push({
                idx:    cells[0].innerText.trim(),
                prompt: cells[1].innerText.trim(),
                stop:   cells[2].innerText.trim(),
                raw:    cells[3].innerText.trim(),
                pass:   cells[4].innerText.trim() === '✓',
                reason: cells[5].innerText.trim(),
            });
        });
        return rows;
    }""")

    print(f"\n  {'#':<4} {'PASS':<5} {'RAW OUTPUT':<38} {'REASON'}")
    print(f"  {'-'*4} {'-'*5} {'-'*38} {'-'*20}")
    for r in results:
        marker = "✓" if r["pass"] else "✗"
        raw_trunc = r["raw"][:36].replace('\n','↵') if r["raw"] else "(empty)"
        print(f"  {r['idx']:<4} {marker:<5} {raw_trunc:<38} {r['reason']}")

    passed = [r for r in results if r["pass"]]
    print(f"\n  PASS: {len(passed)}/{len(results)}")
    print(f"  Good names: {[r['raw'] for r in passed]}")
    return results


def main():
    all_results = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--enable-features=SharedArrayBuffer",
            ]
        )
        context = browser.new_context(
            # Required for SharedArrayBuffer (wllama multi-thread)
            extra_http_headers={
                "Cross-Origin-Embedder-Policy": "require-corp",
                "Cross-Origin-Opener-Policy":   "same-origin",
            }
        )
        page = context.new_page()
        page.set_default_timeout(MODEL_TIMEOUT_MS)

        # Capture console noise for debugging
        page.on("console", lambda m: None)  # suppress to keep output clean
        page.on("pageerror", lambda e: print(f"  PAGE ERROR: {e}"))

        page.goto(URL, wait_until="networkidle")

        for label, sel_value in MODELS:
            results = run_model(page, label, sel_value)
            all_results[label] = results

        browser.close()

    # Summary
    print(f"\n\n{'='*60}")
    print("  SUMMARY — passing names by model")
    print(f"{'='*60}")
    for label, results in all_results.items():
        passed = [r["raw"] for r in results if r["pass"]]
        print(f"\n  {label} ({len(passed)}/{len(results)} passed):")
        for name in passed:
            print(f"    • {name}")

    # Write JSON
    out_path = "/home/mbhat/manojbhat09.github.io/test_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nFull results saved to {out_path}")


if __name__ == "__main__":
    main()
