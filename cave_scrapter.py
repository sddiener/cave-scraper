import sys
import requests
from bs4 import BeautifulSoup
import os
import re


def fetch_webpage_text(url: str) -> tuple[str, str]:
    """
    Fetches the text content and cave name from a given URL.

    This function attempts to extract the main content and cave name from a webpage.
    It uses various selectors to find the main content and falls back to the entire body
    if specific divs are not found. The cave name is extracted from the <h1> tag or <title>.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        tuple[str, str]: A tuple containing two strings:
            - The extracted text content of the webpage.
            - The cave name extracted from the webpage.

    Raises:
        requests.exceptions.RequestException: If there's an error fetching the URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return "", ""

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the main content; adjust the selectors based on the website's structure
    main_content = soup.find('div', {'id': 'main-content'})
    if not main_content:
        main_content = soup.find('div', {'class': 'entry-content'})
    if not main_content:
        main_content = soup.body  # Fallback to entire body if specific div not found

    text = main_content.get_text(separator='\n', strip=True)

    # Extract the cave name from the <h1> tag or <title>
    cave_name = ''
    h1_tag = soup.find('h1')
    if h1_tag:
        cave_name = h1_tag.get_text(strip=True)
    elif soup.title:
        cave_name = soup.title.get_text(strip=True)
    else:
        cave_name = 'cave'  # Default name if none found

    return text, cave_name


def sanitize_filename(name):
    # Remove or replace invalid characters for filenames
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Optional: replace spaces with underscores
    name = name.strip().replace(' ', '_')
    return name


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fetch_cave_info.py <URL>")
        print("Error: URL must be provided as a command-line argument.")
        sys.exit(1)

    url = sys.argv[1]

    text, cave_name = fetch_webpage_text(url)

    sanitized_name = sanitize_filename(cave_name)
    output_filename = f"{sanitized_name}_url_scrape.txt"

    # Save the text to a file in the current directory
    try:
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Content successfully saved to '{output_filename}'")
    except IOError as e:
        print(f"Error writing to file '{output_filename}': {e}")
