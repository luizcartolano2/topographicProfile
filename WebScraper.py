from pyppeteer import launch

from FileManager import FileManager


class WebScraper:
    def __init__(self, url, download_path, headless=True):
        self.url = url
        self.download_path = download_path
        self.headless = headless

    async def __create_browser(self, headless):
        # Create the browser asynchronously
        self.browser = await launch(headless=headless)

    async def close_browser(self):
        # Close the browser asynchronously
        await self.browser.close()

    async def __create_page(self):
        # Create a new page asynchronously
        self.page = await self.browser.newPage()

    async def __set_page_download_behavior(self):
        # Set the download behavior asynchronously
        await self.page._client.send('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': self.download_path
        })

    async def download_file_for_state(self, state):
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
        # This method will be used to run the download process
        await self.download_file_for_state(state)
        await self.close_browser()
