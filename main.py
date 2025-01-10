""" Docstring for the main.py file

"""
import os

import asyncio
from scraper import WebScraper


if __name__ == "__main__":
    # Set the download path
    download_path = f'{os.getcwd()}/files'  # Replace with your desired directory path

    web_scraper = WebScraper(
        url='https://sistemas.anatel.gov.br/se/public/view/b/licenciamento',
        download_path=download_path,
        headless=False
    )

    asyncio.run(web_scraper.run(state="RJ"))
