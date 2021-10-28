from imgurpython import ImgurClient
from urllib.parse import urlparse

# TODO find a better place for these...
client_id = "d54ebc2a8a76634"
client_secret = "fdc101dc5cd3e60b190e41e293be991b170f7022"

client = ImgurClient(client_id, client_secret)


def get_media_from_post(post):
    url_path = urlparse(post.url).path

    # The first part of the link path tells us the type
    link_type = url_path.split("/")[1]
    # The last part tells us the id
    item_id = url_path.split("/")[-1]

    images = []
    links = []

    # If path starts with "a" and does not reference a single image in the album
    if link_type == "a" and "#" not in item_id:
        images = client.get_album_images(item_id)
    elif link_type == "gallery":
        # We don't support galleries
        raise Exception("Unsupported Imgur url.")
    else:
        images = [client.get_image(item_id)]

    # Loop through images to verify they're not ads
    for image in images:
        if not image.is_ad:
            links.append(image.link)

    return links
