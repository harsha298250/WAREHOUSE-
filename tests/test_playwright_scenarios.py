import pytest
import os
from playwright.sync_api import sync_playwright, expect

BASE_URL = os.getenv("PLAYWRIGHT_TEST_URL", "http://127.0.0.1:8000")


def test_scenario_lab_workflow(browser_context):
    page = browser_context.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE_URL)
    
    # 1. Login
    page.fill("#login-username", "admin")
    page.fill("#login-password", "Admin@123")
    page.click("#login-form button[type='submit']")
    page.wait_for_selector("#app-shell.active", timeout=45000)
    
    # Wait for dashboard KPIs to render to avoid navigation race conditions
    page.wait_for_selector(".kpi-card", timeout=45000)
    
    # 2. Navigate to What-If / Scenario Lab Screen
    page.click(".nav-item[data-view='what-if-simulator']")
    
    # Wait for the scenario lab workspace to fully load (async)
    page.wait_for_selector("#tab-scenarios", timeout=10000)
    expect(page.locator("#topbar-title")).to_have_text("Scenarios", timeout=5000)
    
    # Verify manage scenarios tab is active
    expect(page.locator("#tab-scenarios")).to_be_visible()
    
    # Wait for the create scenario form to be available in the DOM
    page.wait_for_selector("#create-scenario-form", timeout=10000)
    page.wait_for_selector("#scen-name", timeout=5000)
    
    # 3. Create a Custom Scenario via Form
    page.fill("#scen-name", "Surge Flow Simulation")
    page.fill("#scen-desc", "Simulating massive incoming orders flow")
    page.fill("#scen-vol", "12")
    page.fill("#scen-freq", "30")
    page.fill("#scen-rob", "5")
    
    # Submit using the specific form's submit button (not the ambiguous generic selector)
    page.click("#create-scenario-form button[type='submit']")
    page.wait_for_timeout(2000)
    
    # 4. Switch to Experiments Tab
    page.click("#tab-experiments")
    
    # Wait for the experiments form and list to fully render
    page.wait_for_selector("#run-experiment-form", timeout=10000)
    expect(page.locator("#run-experiment-form")).to_be_visible()
    
    # 5. Run an Experiment
    page.wait_for_selector("#exp-title", timeout=5000)
    page.fill("#exp-title", "OR-Tools Priority Test")
    page.select_option("#exp-strategy", "OR_TOOLS_ASSIGNMENT")
    page.fill("#exp-rep", "2")
    
    page.click("button:has-text('Queue & Execute')")
    page.wait_for_timeout(2000)
    
    # Verify queue action creates entries in the history list
    expect(page.locator("#experiments-list-container")).to_contain_text("OR-Tools Priority Test", timeout=10000)
    page.close()
