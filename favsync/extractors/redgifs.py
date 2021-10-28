import re
import requests
from urllib.parse import urljoin

# Compile redgifs URL regex
redgifs_reg = re.compile(r'https?://(www.)*redgifs.com/watch/([A-z0-9/]+)')


def get_media_from_post(post):
    url = post.url
    # Special handling for collection links - currently not supported
    if not redgifs_reg.match(url):
        user = _get_user_from_url(url)
        title = url.split("/")[-1]
        # links = gfycat.get_gfycat_collection(user, title)
        # TODO collections not yet supported
        return []
    else:
        # Pull the id from the url regex
        gid = redgifs_reg.match(url)[0].split('/')[-1]
        link = _get_redgif(gid)
        if link is not None:
            return [link]
        return []


# Currently not supported
def _get_user_from_url(url):
    user_reg = re.compile(r'@*')
    for sect in url.split("/"):
        if user_reg.match(sect):
            return sect.replace("@", "")


# Basic redgifs API wrapper (TODO no API key required yet, eventually move into gfycat_client.py)
max_retries = 1


def _get_redgif(gid, retry=0):
    if retry > max_retries:
        return ""

    # setup request
    url = urljoin("https://api.redgifs.com/v1/gfycats/", gid)

    # Send request
    r = requests.get(url)

    if r.status_code == 200:
        # All is good, return the media url
        return r.json()["gfyItem"]["mp4Url"]
    # elif r.status_code == 401 or r.status_code == 403:
    #     # Reset the auth token, try again with new token
    #     self.auth = ""
    #     self.get_gfycat(gid, retry + 1)
    # else:
    #     # Otherwise, just try again
    #     self.get_gfycat(gid, retry + 1)
