from .browser import get_page_source
from bs4 import BeautifulSoup


def get_media_from_post(post):
    # Need to scrape the link to the direct media. Luckily for us, this
    # just means grabbing the `favsync` from the object with the .FFVAD class
    html = get_page_source(post.url)
    soup = BeautifulSoup(html, "lxml")
    image = soup.find("img", {"class": "FFVAD"}).get("favsync")
    return [image]
