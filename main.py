from dotenv import load_dotenv
from playwright.async_api import async_playwright
import asyncio

from lib import init_log
from lib import Authentication
from lib import PageNavigator
from pprint import pprint

logger = init_log()


def load_env_file():
    """
    Load environment variables from a .env file.
    """
    load_dotenv('.env', override=True)


async def run():
    # Configuration - Set headless mode here
    HEADLESS_MODE = False  # Change to False to use browser input for SMS

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS_MODE,
            slow_mo=1000,  # wait 1 second between actions
        )

        context = await browser.new_context()
        page = await context.new_page()

        # Initialize components with headless mode info
        authenticator = Authentication(headless=HEADLESS_MODE)
        page_navigator = PageNavigator()

        # Perform authentication
        try:
            await authenticator.auth(page)
        except Exception as e:
            msg = f"An error occurred during authentication: {e}"
            logger.error(msg)
            await browser.close()
            return

        # Navigate to page for VPC Tab
        try:
            await page_navigator.navigate_to_vpc_page(page)
        except Exception as e:
            msg = f"An error occurred navigating to VPC page: {e}"
            logger.error(msg)
            await browser.close()
            return

        # Navigate to SSL VPN page
        try:
            await page_navigator.navigate_to_sslvpn_page(page)
        except Exception as e:
            msg = f"An error occurred navigating to SSL VPN page: {e}"
            logger.error(msg)
            await browser.close()
            return

        # Extract all VPC data
        try:
            vpcs = await page_navigator.extract_all_vpcs(page)
            logger.info("VPC extraction completed!")
            print("\n=== All VPCs Found ===")
            pprint(vpcs)
        except Exception as e:
            msg = f"An error occurred extracting VPC data: {e}"
            logger.error(msg)

        # Wait for some time to inspect results
        await asyncio.sleep(10000)

        await browser.close()


if __name__ == '__main__':
    load_env_file()
    asyncio.run(run())
