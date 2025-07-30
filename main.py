import os
from typing import Optional
from playwright.sync_api import sync_playwright, Page
from dotenv import load_dotenv
import time

URL = "https://auth.gov-ncloud.com/login"


def load_env_file():
    """
    Load environment variables from a .env file.
    """
    load_dotenv('.env', override=True)


def login(page: Page):
    """
    Perform login to the Naver Cloud Platform using Playwright.
    """
    page.goto(URL)

    # Wait for the login form to load
    page.wait_for_selector("#loginAlias")

    # Fill in the login form
    page.fill('#loginAlias',
              os.getenv('LOGIN_ALIAS'))  # Replace with your username
    page.fill('#username', os.getenv('USERNAME'))  # Replace with your username
    page.fill('#password', os.getenv('PASSWORD'))  # Replace with your username

    # Click the login button
    page.click('button[type="submit"]')

    # Wait for the page to load after login
    page.wait_for_load_state()

    print("Login successful!")


def main():
    load_dotenv()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=1000,  # wait 1 second between actions
            channel="msedge"  # Use Microsoft Edge browser
        )

        context = browser.new_context()
        page = context.new_page()

        login(page)


if __name__ == '__main__':
    main()
