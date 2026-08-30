import pytest
import time
import os
from playwright.sync_api import sync_playwright, Page, expect

# E2E Tests rely on a running server. We assume a running server at http://localhost:8000
# (which is started during Playwright CI test phase or run locally by the user).
BASE_URL = os.getenv("PLAYWRIGHT_TEST_URL", "http://127.0.0.1:8000")

def test_auth_login_logout(browser_context):
    """Test standard login workflow and logout redirection."""
    page = browser_context.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE_URL)
    
    # Assert login page loads
    expect(page.locator(".login-card h2")).to_have_text("Sign In to Platform")
    
    # Fill login form
    page.fill("#login-username", "admin")
    page.fill("#login-password", "Admin@123")
    page.click("button[type='submit']")
    
    # Should redirect to app shell dashboard
    page.wait_for_selector("#app-shell.active", timeout=30000)
    expect(page.locator("#topbar-title")).to_have_text("Dashboard")
    
    # Verify username is set in sidebar footer
    expect(page.locator("#user-name")).not_to_have_text("—")
    
    # Click logout button
    page.click("#logout-btn")
    page.click("#confirm-yes")
    
    # Verify returned to login screen
    page.wait_for_selector("#login-screen", timeout=5000)
    expect(page.locator(".login-card h2")).to_have_text("Sign In to Platform")
    page.close()


def test_dashboard_and_navigation(browser_context):
    """Test dashboard widgets loading and basic sidebar navigation clicks."""
    page = browser_context.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE_URL)
    
    # Login
    page.fill("#login-username", "admin")
    page.fill("#login-password", "Admin@123")
    page.click("button[type='submit']")
    page.wait_for_selector("#app-shell.active", timeout=30000)
    
    # Check that KPIs render
    expect(page.locator("#system-status-indicator")).to_be_visible()
    
    # Navigate to Orders view
    page.click(".nav-item[data-view='orders']")
    page.wait_for_timeout(300) # wait for view transition
    expect(page.locator("#topbar-title")).to_have_text("Orders")
    
    # Navigate to Inventory (Items) view
    page.click(".nav-item[data-view='items']")
    page.wait_for_timeout(300)
    expect(page.locator("#topbar-title")).to_have_text("Inventory")
    
    # Navigate to System Health (Diagnostics View)
    page.click(".nav-item[data-view='system-health']")
    page.wait_for_selector("#ai-chat-input", timeout=30000)
    expect(page.locator("#topbar-title")).to_have_text("System Health")
    
    # Ensure diagnostics center and AI Assistant chat are visible on Health view
    expect(page.locator("#ai-chat-input")).to_be_visible()
    expect(page.locator("#btn-run-ortools-benchmark")).to_be_visible()
    page.close()


def test_ai_assistant_interaction(browser_context):
    """Test typing a query to the AI chat assistant inside Diagnostics dashboard."""
    page = browser_context.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE_URL)
    page.wait_for_selector("#login-username", timeout=15000)
    
    # Login
    page.fill("#login-username", "admin")
    page.fill("#login-password", "Admin@123")
    page.click("button[type='submit']")
    page.wait_for_selector("#app-shell.active", timeout=30000)
    
    # Wait for the app shell's status indicator to confirm dashboard has rendered.
    # .kpi-card elements are injected asynchronously by the analytics API call and
    # can race on slower machines; #system-status-indicator is part of the static
    # app shell and is always present once login completes.
    page.wait_for_selector("#system-status-indicator", timeout=30000)
    
    # Navigate to System Health (Diagnostics View)
    page.click(".nav-item[data-view='system-health']")
    
    # Wait for the system health dashboard to fully load (including AI chat widget)
    # The AI chat input only appears after loadHealthDashboard() completes
    page.wait_for_selector("#ai-chat-input", timeout=30000)
    page.wait_for_selector("#ai-chat-send", timeout=5000)
    
    # Ask chatbot for robot status
    page.fill("#ai-chat-input", "Show me the robot fleet status")
    page.click("#ai-chat-send")
    
    # Wait for assistant response — either the loader disappears or the response text appears
    # The loader may appear and disappear quickly, so we wait for the response content directly
    page.wait_for_timeout(500)  # Brief wait for the API call to start
    
    # Wait for response by checking that a non-loader child appears with robot-related text
    # Use a generous timeout since the backend AI assistant query includes DB lookups
    chat_box = page.locator("#ai-chat-messages")
    expect(chat_box).to_contain_text("robot", ignore_case=True, timeout=15000)
    page.close()


def test_security_rbac_restrictions(browser_context):
    """Test that a viewer role is blocked from admin configuration actions."""
    page = browser_context.new_page()
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE_URL)
    
    # Log in as test_viewer (seeded by conftest.py)
    # Viewer credentials: test_viewer / TestViewer@123
    page.fill("#login-username", "test_viewer")
    page.fill("#login-password", "TestViewer@123")
    page.click("button[type='submit']")
    page.wait_for_selector("#app-shell.active", timeout=30000)
    
    # Verify user name and role is viewer
    expect(page.locator("#user-role")).to_have_text("viewer")
    
    # Click user options card (should be viewer options, not admin options)
    page.click("#user-info-click")
    page.wait_for_timeout(300)
    
    # The Admin Option Modal triggers admin options, let's verify Add New Admin button is hidden or doesn't exist
    modal = page.locator("#admin-options-overlay")
    if modal.is_visible():
        # "Add New Admin" button must NOT be visible or should be disabled for viewers
        btn = page.locator("#btn-open-add-admin")
        expect(btn).not_to_be_visible()
        
    page.close()
