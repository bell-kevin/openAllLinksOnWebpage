import requests
from bs4 import BeautifulSoup
import webbrowser
import time
import os
import platform

def open_all_links(url, browser_name):
    start_time = time.time()
    tabs_opened = 0  # Counter for opened tabs

    print(f"Sending GET request to {url}")
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        print(f"Failed to retrieve the website. Status code: {response.status_code}")
        return []
    print("Request successful")

    soup = BeautifulSoup(response.content, 'html.parser')
    print("Parsed HTML content")

    links = soup.find_all('a', href=True)
    print(f"Found {len(links)} links:")
    for link in links:
        print(link['href'])

    for link in links:
        href = link['href']
        if href.startswith('http'):
            if "github" not in href:
                if not is_unreachable(href):
                    final_url = get_final_url(href)
                    if final_url != href:
                        print(f"Redirected from {href} to {final_url}")
                    num_links = count_links(final_url)
                    print(f"Number of links on {final_url}: {num_links}")
                    if num_links == 0 and "piped" in final_url:
                        print(f"Opening absolute link: {final_url}")
                        open_in_browser(final_url, browser_name)
                        tabs_opened += 1  # Increment the counter
                    else:
                        print(f"Skipping link with {num_links} links or without 'piped': {final_url}")
                else:
                    print(f"Skipping unreachable link: {href}")
            else:
                print(f"Skipping GitHub link: {href}")
        else:
            absolute_url = requests.compat.urljoin(url, href)
            if "github" not in absolute_url:
                if not is_unreachable(absolute_url):
                    final_url = get_final_url(absolute_url)
                    if final_url != absolute_url:
                        print(f"Redirected from {absolute_url} to {final_url}")
                    num_links = count_links(final_url)
                    print(f"Number of links on {final_url}: {num_links}")
                    if num_links == 0 and "piped" in final_url:
                        print(f"Opening relative link: {final_url}")
                        open_in_browser(final_url, browser_name)
                        tabs_opened += 1  # Increment the counter
                    else:
                        print(f"Skipping link with {num_links} links or without 'piped': {final_url}")
                else:
                    print(f"Skipping unreachable link: {absolute_url}")
            else:
                print(f"Skipping GitHub link: {absolute_url}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"Total run time: {int(minutes)} minutes and {int(seconds)} seconds")
    print(f"Total tabs opened: {tabs_opened}")  # Print the total number of tabs opened

    return links

def is_unreachable(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code in [400, 401, 403, 404, 408, 429, 500, 502, 503, 504, 523] or \
           "Hmmm… can't reach this page" in response.text or \
           "This site has been reported as unsafe" in response.text or \
           "Access Denied" in response.text or \
           "403 Forbidden" in response.text:
            return True
    except requests.RequestException:
        return True
    return False

def get_final_url(url):
    try:
        response = requests.get(url, timeout=5)
        return response.url
    except requests.RequestException:
        return url

def count_links(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            return len(links)
        else:
            return 0
    except requests.RequestException:
        return 0

def open_in_browser(url, browser_name):
    # Detect the platform to choose the appropriate browser
    system = platform.system()
    
    if system == 'Windows':
        if browser_name == 'firefox':
            firefox_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'  # Update this path if Firefox is installed elsewhere
            webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))
            webbrowser.get('firefox').open(url)
        elif browser_name == 'chromium':
            chromium_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Adjust if Chromium is installed separately
            webbrowser.register('chromium', None, webbrowser.BackgroundBrowser(chromium_path))
            webbrowser.get('chromium').open(url)
        else:
            webbrowser.open(url)  # Opens with the default browser (usually Edge)
    elif system == 'Linux':
        if browser_name == 'firefox':
            webbrowser.get('firefox').open(url)
        elif browser_name == 'chromium':
            webbrowser.get('chromium').open(url)
        else:
            webbrowser.open(url)
    else:
        webbrowser.open(url)

# Example usage
website_url = 'https://github.com/TeamPiped/Piped/wiki/Instances'
browser_name = input("Which browser would you like to use? (Options: firefox or chromium) ")
links = open_all_links(website_url, browser_name)
