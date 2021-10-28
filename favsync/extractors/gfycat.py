import re
from .gfycat_client import GfycatClient

# Setup gfycat client
gfycat = GfycatClient()

# Compile gfycat URL regex
gfycat_reg = re.compile(r'https?://(www.)*gfycat.com/([A-z0-9/]+)')


def get_media_from_post(post):
    url = post.url
    # Special handling for collection links
    if not gfycat_reg.match(url):
        user = _get_user_from_url(url)
        title = url.split("/")[-1]
        links = gfycat.get_gfycat_collection(user, title)
        return links
    else:
        # Pull the id from the url regex
        gid = gfycat_reg.match(url)[0].split('/')[-1]
        link = gfycat.get_gfycat(gid)
        if link is not None:
            return [link]
        return []


def _get_user_from_url(url):
    user_reg = re.compile(r'@*')
    for sect in url.split("/"):
        if user_reg.match(sect):
            return sect.replace("@", "")
