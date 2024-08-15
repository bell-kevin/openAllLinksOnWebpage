import requests
from bs4 import BeautifulSoup
import webbrowser

def open_all_links(url):
    print(f"Sending GET request to {url}")
    # Send a GET request to the website
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the website. Status code: {response.status_code}")
        return
    print("Request successful")
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    print("Parsed HTML content")
    
    # Find all the anchor tags with href attributes
    links = soup.find_all('a', href=True)
    
    # Print the links for debugging
    print(f"Found {len(links)} links:")
    for link in links:
        print(link['href'])
    
    # Open each link in the web browser, skipping GitHub links
    for link in links:
        href = link['href']
        # Check if the link is absolute or relative
        if href.startswith('http'):
            if "github.com" not in href:
                print(f"Opening absolute link: {href}")
                webbrowser.open(href)
            else:
                print(f"Skipping GitHub link: {href}")
        else:
            # Construct the absolute URL for relative links
            absolute_url = requests.compat.urljoin(url, href)
            if "github.com" not in absolute_url:
                print(f"Opening relative link: {absolute_url}")
                webbrowser.open(absolute_url)
            else:
                print(f"Skipping GitHub link: {absolute_url}")

# Example usage
website_url = 'https://github.com/TeamPiped/Piped/wiki/Instances'
open_all_links(website_url)

