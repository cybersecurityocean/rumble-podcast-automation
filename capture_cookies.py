#!/usr/bin/env python3
"""
Rumble Cookie Capture Tool
Opens a browser, lets you log in manually, then saves clean cookies.
"""
import json
import sys
import os

def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: pip install playwright && playwright install chromium")
        sys.exit(1)

    print("=" * 60)
    print("  RUMBLE COOKIE CAPTURE")
    print("=" * 60)
    print()
    print("  1. A browser window will open")
    print("  2. Log in to Rumble manually")
    print("  3. Once logged in, come back here and press Enter")
    print("  4. Cookies will be saved as clean JSON")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://rumble.com/login")
        print("  Browser opened. Log in now...")
        print()

        input("  Press ENTER after you've logged in successfully...")

        # Navigate to dashboard to confirm login
        page.goto("https://rumble.com/account/videos", wait_until="networkidle")
        import time
        time.sleep(2)

        title = page.title()
        url = page.url
        print(f"  Current page: {url}")
        print(f"  Page title: {title}")

        if "login" in url.lower() or "auth" in url.lower():
            print()
            print("  WARNING: It looks like you're NOT logged in.")
            print("  Please log in and press Enter again.")
            input("  Press ENTER when ready...")

        cookies = context.cookies()
        browser.close()

    if not cookies:
        print("  ERROR: No cookies captured.")
        sys.exit(1)

    # Filter to only rumble.com cookies (skip ad trackers, etc.)
    rumble_cookies = [c for c in cookies if "rumble.com" in c.get("domain", "")]
    all_cookies = cookies

    print(f"\n  Total cookies: {len(all_cookies)}")
    print(f"  Rumble cookies: {len(rumble_cookies)}")

    # Save clean JSON (single line, no control characters)
    # Playwright cookies have extra fields we don't need - strip to essentials
    clean_cookies = []
    for c in all_cookies:
        clean = {
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c.get("path", "/"),
        }
        if c.get("httpOnly"):
            clean["httpOnly"] = True
        if c.get("secure"):
            clean["secure"] = True
        if c.get("sameSite"):
            clean["sameSite"] = c["sameSite"]
        clean_cookies.append(clean)

    json_str = json.dumps(clean_cookies, separators=(',', ':'))

    # Verify it parses back correctly
    parsed = json.loads(json_str)
    assert len(parsed) == len(clean_cookies), "JSON round-trip failed!"

    # Save to file
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rumble_cookies.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json_str)

    print(f"\n  Saved to: {out_path}")
    print(f"  JSON size: {len(json_str)} chars")
    print()
    print("=" * 60)
    print("  NEXT STEPS:")
    print("=" * 60)
    print()
    print("  1. Go to: https://github.com/imthi92/rumble-podcast-automation/settings/secrets/actions")
    print("  2. Delete existing RUMBLE_COOKIES if any")
    print("  3. Click 'New repository secret'")
    print("  4. Name: RUMBLE_COOKIES")
    print(f"  5. Value: copy the contents of {out_path}")
    print("  6. Click 'Add secret'")
    print()
    print("  Key cookies to verify (should be present):")
    key_names = ["a_s", "e_s", "u_s", "ui_t"]
    for name in key_names:
        found = any(c["name"] == name for c in rumble_cookies)
        status = "FOUND" if found else "MISSING"
        print(f"    {name}: {status}")

if __name__ == "__main__":
    main()
