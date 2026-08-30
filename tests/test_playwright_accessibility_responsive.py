import pytest
import os
from playwright.sync_api import expect

BASE_URL = os.getenv("PLAYWRIGHT_TEST_URL", "http://127.0.0.1:8000")

def test_responsive_layout_and_accessibility(browser_context):
    console_logs = []
    
    # Open browser context (Desktop initially)
    page = browser_context.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.on("console", lambda msg: console_logs.append(f"CONSOLE [{msg.type}]: {msg.text}"))
    page.on("pageerror", lambda err: console_logs.append(f"PAGE ERROR: {err}"))
    
    try:
        page.goto(BASE_URL, wait_until="networkidle")
        
        # Verify skip-link accessibility helper is in DOM
        skip_link = page.locator("a.skip-link")
        expect(skip_link).to_be_attached()
        
        # Login
        page.fill("#login-username", "admin")
        page.fill("#login-password", "Admin@123")
        page.click("#login-form button[type='submit']")
        
        # Wait for app active shell
        page.wait_for_selector("#app-shell.active", timeout=45000)
        
        # Wait for dashboard KPIs to render to ensure layout stability
        page.wait_for_selector(".kpi-card", timeout=45000)
        
        # ----------------------------------------------------
        # 1. Desktop Verification (1440x900)
        # ----------------------------------------------------
        sidebar = page.locator("#sidebar")
        expect(sidebar).to_be_visible()
        
        # Verify no horizontal scrollbar exists on desktop body
        overflow_ok = page.evaluate("document.body.clientWidth >= document.documentElement.scrollWidth")
        assert overflow_ok, "Desktop viewport has horizontal page overflow!"
        
        # ----------------------------------------------------
        # 2. Tablet Verification (768x1024)
        # ----------------------------------------------------
        page.set_viewport_size({"width": 768, "height": 1024})
        page.wait_for_timeout(500) # Allow resize CSS reflows
        
        # Mobile menu button should be visible
        menu_btn = page.locator("#mobile-menu-btn")
        expect(menu_btn).to_be_visible()
        
        # Click menu button to show sidebar drawer
        menu_btn.click()
        page.wait_for_timeout(500) # Allow CSS transitions to slide drawer
        
        # Sidebar should have class 'open'
        expect(sidebar).to_have_class("sidebar open")
        
        # Close sidebar drawer with close button
        close_btn = page.locator("#sidebar-close-btn")
        expect(close_btn).to_be_visible()
        close_btn.click()
        page.wait_for_timeout(500)
        
        # Class 'open' should be removed
        expect(sidebar).not_to_have_class("sidebar open")
        
        # Verify no horizontal scrollbar exists on tablet body
        overflow_ok = page.evaluate("document.body.clientWidth >= document.documentElement.scrollWidth")
        assert overflow_ok, "Tablet viewport has horizontal page overflow!"
        
        # ----------------------------------------------------
        # 3. Mobile Verification (390x844)
        # ----------------------------------------------------
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(500) # Allow resize CSS reflows
        
        # Verify topbar menu toggle is present
        expect(page.locator("#mobile-menu-btn")).to_be_visible()
        
        # Verify no horizontal scrollbar exists on mobile body
        overflow_ok = page.evaluate("document.body.clientWidth >= document.documentElement.scrollWidth")
        assert overflow_ok, "Mobile viewport has horizontal page overflow!"
        
        page.close()
    except Exception as e:
        page.screenshot(path="responsive_failed.png")
        print("\n=== CONSOLE LOGS ===")
        for log in console_logs:
            print(log)
        print("====================")
        page.close()
        raise e
