import requests
from urllib.parse import urljoin

# TODO find better place for these
client_id = "2_SYdC8h"
client_secret = "eP5t3claGHI0ZPxPzYSsieIq7agfre16nqJ-GagGIHkl_iDuY1mAXN6Qto249UwG"

max_retries = 1


class GfycatClient:
    auth = ""

    def __init__(self):
        # Setup auth token
        self.get_bearer_token()

    def get_bearer_token(self):
        # Setup request
        url = "https://api.gfycat.com/v1/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }

        # Send request for auth token
        r = requests.post(url, json=payload)

        if r.status_code == 200:
            self.auth = r.json()["access_token"]

    def get_gfycat(self, gid, retry=0):
        if retry > max_retries:
            return ""

        if self.auth == "":
            self.get_bearer_token()

        # setup request
        url = urljoin("https://api.gfycat.com/v1/gfycats/", gid)
        headers = {
            "Authorization": "Bearer " + self.auth
        }

        # Send request
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            # All is good, return the webm url
            return r.json()["gfyItem"]["webmUrl"]
        elif r.status_code == 401 or r.status_code == 403:
            # Reset the auth token, try again with new token
            self.auth = ""
            self.get_gfycat(gid, retry + 1)
        else:
            # Otherwise, just try again
            self.get_gfycat(gid, retry + 1)

    def get_gfycat_collection(self, user, title, retry=0):
        if retry > max_retries:
            return []

        if self.auth == "":
            self.get_bearer_token()

        # setup request
        url = "https://api.gfycat.com/v1/users/" + user + "/album_links/" + title
        headers = {
            "Authorization": "Bearer " + self.auth
        }

        # Send request
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            # All is good, return the webm urls
            urls = []
            for gfy in r.json()["publishedGfys"]:
                urls.append(gfy["webmUrl"])
            return urls
        elif r.status_code == 401 or r.status_code == 403:
            # Reset the auth token, try again with new token
            self.auth = ""
            self.get_gfycat(id, retry + 1)
        else:
            # Otherwise, just try again
            self.get_gfycat(id, retry + 1)
