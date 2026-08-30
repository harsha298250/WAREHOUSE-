import pytest
import os
from playwright.sync_api import sync_playwright, expect

BASE_URL = os.getenv("PLAYWRIGHT_TEST_URL", "http://127.0.0.1:8000")


def test_system_health_dashboard_workflow(browser_context):
    page = browser_context.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    
    # Capture console messages for diagnostics
    console_logs = []
    page.on("console", lambda msg: console_logs.append(f"CONSOLE [{msg.type}]: {msg.text}"))
    page.on("pageerror", lambda err: console_logs.append(f"PAGE ERROR: {err}"))
    
    try:
        page.goto(BASE_URL, wait_until="networkidle")
        
        # 1. Login with postgres database admin credentials
        page.fill("#login-username", "admin")
        page.fill("#login-password", "Admin@123")
        page.click("#login-form button[type='submit']")
        
        # Wait to allow async bootstrapApp steps
        page.wait_for_selector("#app-shell.active", timeout=45000)
        
        # Wait for dashboard KPIs to render to avoid navigation race conditions
        page.wait_for_selector(".kpi-card", timeout=45000)
        
        # 2. Navigate to System Health
        page.click(".nav-item[data-view='system-health']")
        
        # Wait for the main observability center view container or heading to be visible
        page.wait_for_selector("h2:has-text('System Observability & Diagnostic Center')", timeout=20000)
        
        # Wait for the health dashboard content to fully load (async API calls)
        # The PLATFORM STATUS badge only appears after loadHealthDashboard() completes
        page.wait_for_selector("strong:has-text('PLATFORM STATUS')", timeout=45000)
        
        # 3. Check dependencies details table — wait for the actual data table content
        page.wait_for_selector("table.data-table", timeout=10000)
        
        # Wait specifically for the PostgreSQL Database row to render
        # This is inside the template literal and renders after API response
        page.wait_for_selector("td strong:has-text('PostgreSQL Database')", timeout=10000)
        expect(page.locator("td strong:has-text('PostgreSQL Database')")).to_be_visible()
        
        # 4. Check that incidents section loads
        expect(page.locator("#incidents-container")).to_be_visible()
        
        # 5. Check threshold configs inputs are present
        expect(page.locator("#thresholds-config-form")).to_be_visible()
        
        # 6. Change a threshold value and submit
        # Wait for async thresholds API data to populate the form inputs
        page.wait_for_selector("input[name='api_latency_warning_ms']", timeout=10000)
        input_field = page.locator("input[name='api_latency_warning_ms']")
        expect(input_field).to_be_visible()
        input_field.fill("350.0")
        
        # Click save configuration button
        page.click("button:has-text('Save Configurations')")
        page.wait_for_timeout(1000)
        
    except Exception as e:
        # Take diagnostic screenshot on any failure
        page.screenshot(path="system_health_failed.png")
        print("\n=== BROWSER CONSOLE LOGS ===")
        for log in console_logs:
            print(log)
        print("=============================")
        raise e
    finally:
        page.close()
