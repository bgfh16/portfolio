# BeautifulSoup - used to parse and extract data from the HTML (like finding the title and body of the page)
# requests - used to fetch the webpage (like opening the URL)
from bs4 import BeautifulSoup
import requests
# urlparse breaks a URL into parts, and urlunparse rebuilds it back into a full URL.
# This is used because sometimes you want to change ONE part of the URL only.
from urllib.parse import urlparse, urlunparse


# Standard headers to fetch a website
# Pretends your request is coming from a real browser (like Chrome)
# Some websites block bots - this helps avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Takes a url (string) and returns a cleaned/normalized URL (string)
# url: str - means that the input should be a string
# -> str - means that the output will be a string. Nothing fancy, just for readability and better
# code understanding

# _normalize_url() is an internal helper by convention (indicated by _) 
# and it's meant to be used inside its module, while other files should only use 
# the module’s public functions, although Python does not strictly enforce this.
# We use _ to mark internal functions so developers know what is safe to use externally and what is 
# meant to stay hidden as implementation detail. Implementation details are the hidden internal 
# steps that make a function work, and while they’re not enforced as private in Python, it’s best practice 
# to keep them internal so users only interact with the simple, public function instead of the inner workings.
# For example (This example explains implementation detail better): When you import scraper.py into another file, 
# you should only use the main functions it exposes (like fetch_website_contents()), not its internal 
# helper functions (like _normalize_url()), because those helpers are meant for internal use and may change without warning.
def _normalize_url(url: str) -> str:
    """
    Normalize known problematic hostnames/URLs so scraping doesn't fail.

    """
    # This attempts to break the URL into parts. If something goes wrong, 
    # we are telling the code to just return the original URL. It's basically a safety mechanism
    # to prevent the code from crashing while scrapping
    try:
        parsed = urlparse(url)
    except Exception:
        return url
    # .netloc references the name of the site we are trying to scrape
    # .lower() make it lowercase (obviously) to use while comparing
    # We are comparing the domain of the URL we received vs a known problematic domain we want to fix
    # We are checking if this URL is from a domain we know is problematic and should be replaced.
    # blog.huggingface.co doesn't work well in some environments so this section converts it to
    # https://huggingface.co/blog for example
    if parsed.netloc.lower() == "blog.huggingface.co":
    # This is what gets returned if line 50 evalutes to true
        return "https://huggingface.co/blog"

    # This is what gets returned if line 50 evalutes to false
    # returns the URL after it has been put back together
    return urlunparse(parsed)


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit

    """
    # Line 67 to 77 does this: This code tries to download a webpage safely, 
    # and if it fails, it doesn’t crash the program, it just skips it.
    url = _normalize_url(url) # This cleans/fixes the URL first. Example: it turns messy or known-bad URLs into safe ones
    try:
        # Sends a request to the URL
        # Returns the webpage content (HTML)
        # Waits max 20 seconds
        response = requests.get(url, headers=headers, timeout=20)
        # This checks if we got a valid response or not. If we didn't, it throws an error
        response.raise_for_status()
    except requests.RequestException as e:
        # Don't let one bad link kill the whole scrape, just skip it and tell us what error was returned
        return f"Skipped: {url}\n\n{type(e).__name__}: {e}"
    # Sends a request to the URL
    # Returns the webpage content (HTML)
    # Converts raw HTML into a structured object
    # Now you can easily extract elements (title, body, etc.)
    soup = BeautifulSoup(response.content, "html.parser")
    # If the page has a <title> - get it
    # If not - fallback to "No title found"
    title = soup.title.string if soup.title else "No title found"
    # Checks if the page has a <body> section 
    # and if it does, it removes all the irrelevant elements (like scripts, styles, images, inputs)
    # then it gets the text content of the body
    # and if the body is not found, it returns an empty string
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        # separator="\n" - puts each element on a new line
        # strip=True - removes extra spaces
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]

# Extract all links (<a href="...">) from a webpage
def fetch_website_links(url):
    """
    Return the links on the webiste at the given url

    """
    # Line 107 to 112's explanation is basically the same as line 67 to 77's explanation
    url = _normalize_url(url)
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException:
        return []
    soup = BeautifulSoup(response.content, "html.parser")
    # Finds all <a> tags
    # Extracts their href attribute
    links = [link.get("href") for link in soup.find_all("a")]
    # Filters out any links that are empty
    # and returns the list of links
    return [link for link in links if link]