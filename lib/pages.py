import os
import logging
from typing import List, Dict, Any

from playwright.async_api import Page
from lib import init_log


class PageNavigationError(Exception):
    """Custom exception for page navigation failures"""

    def __init__(self, message="Page navigation failed"):
        super().__init__(message)


class PageNavigator:
    """
    Page navigation class for handling various page operations in Naver Cloud Platform
    """

    def __init__(self, logger: logging.Logger = None):
        # Use provided logger or create new one if none provided
        self.logger = logger if logger is not None else init_log()

    async def navigate_to_vpc_page(self, page: Page) -> None:
        """
        Navigate to the VPC page through console dashboard
        
        Args:
            page (Page): Playwright page instance
            
        Raises:
            PageNavigationError: If navigation fails
        """
        try:
            # Go to the Console page
            self.logger.info('Navigating to the Console page...')
            await page.goto(os.getenv('CONSOLE_URL'))

            # Handle popup removal
            await self._remove_popup_if_exists(page)

            # Navigate to VPC page
            self.logger.info('Navigating to the VPC page...')
            await page.click(
                selector='#aside > div.lnb.gov-lnb > div.extend > div.platform > a > div > button.btn.btn-sm.flat.btn-platform.vpc'
            )

            # Wait for the page to load completely
            await page.wait_for_load_state()
            self.logger.info('VPC page loaded successfully!')

        except Exception as e:
            self.logger.error(f"Failed to navigate to VPC page: {str(e)}")
            raise PageNavigationError(f"VPC page navigation failed: {str(e)}")

    async def navigate_to_sslvpn_page(self, page: Page) -> None:
        """
        Navigate directly to the SSL VPN page
        
        Args:
            page (Page): Playwright page instance
            
        Raises:
            PageNavigationError: If navigation fails
        """
        try:
            self.logger.info('Going to the SSL VPN page...')
            await page.goto(os.getenv('SSL_VPN_CONSOLE_URL'))
            await page.wait_for_load_state()
            self.logger.info('SSL VPN page loaded successfully!')

        except Exception as e:
            self.logger.error(f"Failed to navigate to SSL VPN page: {str(e)}")
            raise PageNavigationError(
                f"SSL VPN page navigation failed: {str(e)}")

    async def extract_all_vpcs(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract all VPC data from the SSL VPN page
        
        Args:
            page (Page): Playwright page instance
            
        Returns:
            List[Dict[str, Any]]: List of VPC data dictionaries
            
        Raises:
            PageNavigationError: If VPC extraction fails
        """
        try:
            self.logger.info('Extracting all VPC data from the page...')

            # Wait for the VPC table to load
            await page.wait_for_selector(
                '#app > div > div.ph-30.page-body > div.scroll-tbl > div.tbody > table > tbody',
                timeout=10000
            )

            # Get all VPC rows
            vpc_rows = await page.query_selector_all(
                '#app > div > div.ph-30.page-body > div.scroll-tbl > div.tbody > table > tbody > tr'
            )

            vpcs = []

            for i, row in enumerate(vpc_rows):
                try:
                    # Extract VPC name from the second column
                    vpc_name_element = await row.query_selector(
                        'td:nth-child(2) > span')
                    if vpc_name_element:
                        vpc_name = await vpc_name_element.text_content()

                        # Extract additional VPC information from other columns
                        vpc_data = {
                            'name': vpc_name.strip() if vpc_name else '',
                            'row_index': i + 1
                        }

                        # Extract other column data if available
                        columns = await row.query_selector_all('td')
                        for j, col in enumerate(columns):
                            col_text = await col.text_content()
                            vpc_data[
                                f'column_{j + 1}'] = col_text.strip() if col_text else ''

                        vpcs.append(vpc_data)
                        self.logger.info(f'Found VPC: {vpc_name}')

                except Exception as e:
                    self.logger.warning(
                        f'Error extracting VPC data from row {i + 1}: {e}')
                    continue

            self.logger.info(f'Total VPCs found: {len(vpcs)}')
            return vpcs

        except Exception as e:
            self.logger.error(f"Failed to extract VPC data: {str(e)}")
            raise PageNavigationError(f"VPC extraction failed: {str(e)}")

    async def _remove_popup_if_exists(self, page: Page) -> None:
        """
        Remove popup if it exists on the console page
        
        Args:
            page (Page): Playwright page instance
        """
        self.logger.info('Removing the popup if it exists...')

        try:
            await page.wait_for_selector(
                selector='#mCSB_6_container > div > div > label > input[type=checkbox]',
                timeout=5000
            )
            self.logger.info(
                'Popup checkbox found, clicking it to remove the popup...')
            await page.click(
                selector='#mCSB_6_container > div > div > label > input[type=checkbox]'
            )
            await page.click(selector='#mCSB_6_container > div > div > a')
            self.logger.info('Popup removed successfully!')

        except TimeoutError:
            self.logger.info('Popup checkbox not found, no popup to remove.')
        except Exception as e:
            self.logger.error(
                f'An error occurred while trying to remove the popup: {e}')
            raise
