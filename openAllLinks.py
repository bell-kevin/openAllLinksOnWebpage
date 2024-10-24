import asyncio
import aiohttp
from bs4 import BeautifulSoup
import webbrowser
import time
import platform
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configuration for browser paths
BROWSER_PATHS = {
    'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
    'chromium': r'C:\Program Files\Google\Chrome\Application\chrome.exe'
}

async def fetch(session, url):
    """Fetch a URL asynchronously."""
    try:
        async with session.get(url, timeout=10) as response:
            return response.status, await response.text(), str(response.url)  # Convert URL to string
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None, None, url

async def open_all_links(url: str, browser_name: str) -> list:
    """Open all valid links from the given URL in the specified browser."""
    start_time = time.time()
    tabs_opened = 0

    async with aiohttp.ClientSession() as session:
        status, content, _ = await fetch(session, url)

        if status != 200:
            logging.error(f"Failed to retrieve the website. Status code: {status}")
            return []

        logging.info("Request successful")
        soup = BeautifulSoup(content, 'html.parser')
        links = soup.find_all('a', href=True)
        logging.info(f"Found {len(links)} links.")

        tasks = [process_link(session, link['href'], browser_name) for link in links]
        results = await asyncio.gather(*tasks)

        # Count the number of tabs opened
        tabs_opened = sum(results)

    elapsed_time = time.time() - start_time
    logging.info(f"Total run time: {elapsed_time:.2f} seconds")
    logging.info(f"Total tabs opened: {tabs_opened}")

    return links

async def process_link(session, href: str, browser_name: str) -> int:
    """Process a single link: check if it's reachable and open it if valid."""
    if href.startswith('http') and "github" not in href:
        if not await is_unreachable(session, href):
            final_url = await get_final_url(session, href)
            num_links = await count_links(session, final_url)
            # Check if the final URL contains "piped" and has no links
            if num_links == 0 and "piped" in final_url:
                logging.info(f"Opening link: {final_url}")
                open_in_browser(final_url, browser_name)
                return 1  # Increment the count of opened tabs
            else:
                logging.info(f"Skipping link with {num_links} links or without 'piped': {final_url}")
        else:
            logging.info(f"Skipping unreachable link: {href}")
    return 0  # No tab opened

async def is_unreachable(session, url: str) -> bool:
    """Check if a URL is unreachable."""
    status_codes = {400, 401, 403, 404, 408, 429, 500, 502, 503, 504, 523}
    status, _, _ = await fetch(session, url)
    return status in status_codes or status is None

async def get_final_url(session, url: str) -> str:
    """Get the final URL after any redirects."""
    status, _, final_url = await fetch(session, url)
    return final_url if status == 200 else url

async def count_links(session, url: str) -> int:
    """Count the number of links on a given URL."""
    status, content, _ = await fetch(session, url)
    if status == 200:
        soup = BeautifulSoup(content, 'html.parser')
        return len(soup.find_all('a', href=True))
    return 0

def open_in_browser(url: str, browser_name: str):
    """Open a URL in the specified browser."""
    system = platform.system()
    if system == 'Windows':
        if browser_name in BROWSER_PATHS:
            webbrowser.register(browser_name, None, webbrowser.BackgroundBrowser(BROWSER_PATHS[browser_name]))
            webbrowser.get(browser_name).open(url)
        else:
            webbrowser.open(url)  # Opens with the default browser
    elif system == 'Linux':
        if browser_name in BROWSER_PATHS:
            webbrowser.get(browser_name).open(url)
        else:
            webbrowser.open(url)
    else:
        webbrowser.open(url)

# Example usage
if __name__ == "__main__":
    website_url = 'https://github.com/TeamPiped/Piped/wiki/Instances'
    browser_name = input("Which browser would you like to use? (Options: firefox or chromium) ")
    asyncio.run(open_all_links(website_url, browser_name))
