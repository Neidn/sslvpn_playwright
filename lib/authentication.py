import asyncio
import os
import logging

from playwright.async_api import Page

from lib import init_log


class AuthenticationError(Exception):
    """Custom exception for authentication failures"""

    def __init__(self,
        message="Authentication failed. Please check your credentials and try again."):
        super().__init__(message)


class Authentication:
    """
    Authentication class for handling Naver Cloud Platform login and SMS authentication
    """

    def __init__(self, logger: logging.Logger = None, headless: bool = True):
        # Use provided logger or create new one if none provided
        self.logger = logger if logger is not None else init_log()
        self.headless = headless
        self.url = os.getenv('AUTH_URL')
        self.login_alias = os.getenv('LOGIN_ALIAS')
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')

        # Validate environment variables
        if not all([self.login_alias, self.username, self.password]):
            raise AuthenticationError(
                "Missing required environment variables: LOGIN_ALIAS, USERNAME, PASSWORD")

    async def auth(self, page: Page) -> None:
        """
        Perform complete authentication flow including login and SMS verification
        
        Args:
            page (Page): Playwright page instance
            
        Raises:
            AuthenticationError: If authentication process fails
        """
        try:
            self.logger.info('Starting the authentication process...')

            # Step 1: Perform initial login
            await self._login(page)

            # Step 2: Handle SMS authentication
            self.logger.info('Starting SMS authentication...')
            await self._sms_authentication(page)

            self.logger.info('Authentication completed successfully!')

        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationError(
                f"Authentication process failed: {str(e)}")

    async def _login(self, page: Page) -> None:
        """
        Perform initial login to the Naver Cloud Platform
        
        Args:
            page (Page): Playwright page instance
        """
        self.logger.info('Going to the login page...')
        await page.goto(self.url)

        # Wait for the login form to load
        await page.wait_for_selector("#loginAlias", timeout=10000)

        # Fill in the login form
        self.logger.info('Filling in the login credentials...')
        await page.fill(selector='#loginAlias', value=self.login_alias)
        await page.fill(selector='#username', value=self.username)
        await page.fill(selector='#passwordPlain', value=self.password)

        # Click the login button
        self.logger.info('Submitting login form...')
        await page.click(selector='#loginForm > button')

        # Wait for the page to load after login
        await page.wait_for_load_state()

        self.logger.info('Initial login completed successfully!')

    async def _sms_authentication(self, page: Page) -> None:
        """
        Handle SMS two-factor authentication with support for both headless and non-headless modes
        
        Args:
            page (Page): Playwright page instance
        """
        try:
            self.logger.info('Initiating SMS authentication...')

            # Click the SMS authentication button
            await page.click(
                selector='#app > div.popup > div.panel.certi > div.content > div:nth-child(3) > div.btn-wrap > a'
            )

            # Handle any dialogs that may appear
            self.logger.info('Setting up dialog handler...')
            page.once('dialog',
                      lambda dialog: asyncio.create_task(dialog.dismiss())
                      if dialog.type == 'alert' else None)

            if self.headless:
                # Headless mode: Get SMS code programmatically and fill it
                await self._headless_sms_input(page)
            else:
                # Non-headless mode: Wait for user to manually input in browser
                await self._browser_sms_input(page)

            # Click the final login button after entering the code
            self.logger.info('Submitting SMS authentication code...')
            await page.click(selector='#loginForm > a')

            # Wait for the authentication to complete
            await page.wait_for_load_state()

            self.logger.info('SMS authentication completed successfully!')

        except Exception as e:
            self.logger.error(f"SMS authentication failed: {str(e)}")
            raise AuthenticationError(f"SMS authentication failed: {str(e)}")
    
    async def _headless_sms_input(self, page: Page) -> None:
        """
        Handle SMS input in headless mode (CLI input or env variable)
        
        Args:
            page (Page): Playwright page instance
        """
        # Get SMS code via console input or environment variable
        sms_code = await self._get_sms_code()
        
        # Fill the SMS code input field
        self.logger.info('Filling SMS authentication code...')
        await page.fill(
            selector='#loginForm > div > input[type=text]',
            value=sms_code
        )
    
    async def _browser_sms_input(self, page: Page) -> None:
        """
        Handle SMS input in non-headless mode (manual browser input)
        
        Args:
            page (Page): Playwright page instance
        """
        # Wait for the user to manually input the authentication code in browser
        self.logger.info('Please check your phone for the SMS code and enter it in the browser.')
        self.logger.info('Waiting for SMS authentication code input in browser (timeout: 60 seconds)...')
        
        await page.wait_for_function(
            "document.querySelector('#loginForm > div > input[type=text]').value.length > 5",
            timeout=60000
        )
        
        self.logger.info('SMS code detected in browser input field.')
    
    async def _get_sms_code(self) -> str:
        """
        Get SMS code from environment variable or console input
        
        Returns:
            str: The SMS authentication code
        """
        # Option 1: Check environment variable first
        sms_code = os.getenv('SMS_CODE')
        if sms_code:
            self.logger.info('Using SMS code from environment variable')
            return sms_code
        
        # Option 2: Get from console input
        self.logger.info('SMS code not found in environment. Please check your phone for the SMS code.')
        
        # Use asyncio to handle console input without blocking
        loop = asyncio.get_event_loop()
        sms_code = await loop.run_in_executor(
            None, 
            lambda: input("Enter SMS authentication code: ").strip()
        )
        
        # Validate the code
        if not sms_code or len(sms_code) < 4:
            raise AuthenticationError("Invalid SMS code provided")
        
        return sms_code
