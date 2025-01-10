""" Docstring for the web_scraper.py file.

"""
import logging

from pyppeteer import launch
from .file_manager import FileManager


class WebScraper:
    """
    This module defines the WebScraper class, which automates the process of scraping a webpage, applying a filter,
    and downloading the resulting file. It uses the pyppeteer library to interact with the page and manage downloads.
    """
    def __init__(self, url: str, download_path: str, headless: bool = True):
        """
        Constructor for the WebScraper class. It initializes the scraper with the URL to scrape, the download path, and
        an optional flag to run the browser in headless mode.

        :param url: The URL of the webpage to scrape.
        :param download_path: The path where the downloaded file will be saved.
        :param headless: Whether to run the browser in headless mode (no UI). Default is True.
        """
        self.url = url
        self.download_path = download_path
        self.headless = headless
        self.browser = None
        self.page = None
        self.logger = logging.getLogger(__name__)

    async def __create_browser(self, headless: bool):
        """
        Creates a new browser instance asynchronously using the pyppeteer library.

        :param headless: Whether to run the browser in headless mode.
        """
        # Create the browser asynchronously
        self.browser = await launch(headless=headless)

    async def close_browser(self):
        """
        Closes the browser instance asynchronously.
        """
        # Close the browser asynchronously
        await self.browser.close()

    async def __create_page(self):
        """
        Creates a new page instance in the browser asynchronously.
        """
        # Create a new page asynchronously
        self.page = await self.browser.newPage()

    async def __set_page_download_behavior(self):
        """
        Sets the behavior for handling downloads asynchronously. It configures the page to allow downloads and
        specifies the download path.
        """
        # Set the download behavior asynchronously
        # pylint: disable=protected-access
        await self.page._client.send('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': self.download_path
        })

    async def download_file_for_state(self, state: str):
        """
        Downloads a file for a specific state by interacting with the webpage, applying the state filter,
        and downloading the results as a CSV file.

        :param state: The state to filter by on the webpage.
        """
        file_manager = FileManager(self.download_path, 'csv_', '.csv')

        await self.__create_browser(headless=self.headless)
        await self.__create_page()
        await self.__set_page_download_behavior()

        # Go to page url
        await self.page.goto(self.url)

        # Wait for the page to load
        await self.page.waitForSelector("#tblFilter > span:nth-child(5)")
        await self.page.click("#tblFilter > span:nth-child(5)")

        # Apply the filter
        await self.page.waitForSelector("#fc_8")
        await self.page.select('#fc_8', state)

        # Wait for the filter to apply and results to load
        await self.page.waitFor(3000)  # Adjust based on the website's response time

        # Click the download button
        await self.page.click("#download_csv")  # Replace with the actual selector for the download button

        # Check if the file was downloaded
        filename = file_manager.wait_for_download()
        file_manager.unzip_and_rename(filename, f'antennas-{state}.csv')

    async def run(self, state):
        """
        Runs the complete process for downloading the file for the specified state. This includes launching the browser,
        applying the filter, and downloading the file, then closing the browser.

        :param state: The state to filter by on the webpage.
        """
        # This method will be used to run the download process
        await self.download_file_for_state(state)
        await self.close_browser()
