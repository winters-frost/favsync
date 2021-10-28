def get_media_from_post(post):
    gallery = []
    for img in post.media_metadata.items():
        url = img[1]['p'][0]['u']
        url = url.split("?")[0].replace("preview", "i")
        gallery.append(url)

    return gallery
