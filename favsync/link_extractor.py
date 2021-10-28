from os import path
import traceback
from urllib.parse import urlparse
import logging
from extractors import gfycat, redgifs, instagram, imgur, reddit_gallery

accepted_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webm", ".mp4", ".gifv"]
enable_ytdl = False

# Site enums
GFYCAT = 0
REDGIFS = 1
IMGUR = 2
VREDDIT = 3
INSTAGRAM = 4
YTDL = 5
RGALLERY = 6


def extract_media_links(saved_list, remove_saved=False):
    """Extracts the direct links to the media contained within each saved post"""
    links = []
    for post in saved_list:
        site_links = _extract_media_link(post, remove_saved)
        if len(site_links) > 0:
            entry = {"post": post, "links": site_links}
            links.append(entry)
        else:
            logging.warning(f"No supported media found in post ID: {post.id}. Post URL: {post.url}")

    return links


def _extract_media_link(post, remove_saved):
    """Extracts the direct media link given the site page"""
    url = post.url
    # Direct links to media require no pre-processing
    if _is_direct_media_link(url):
        return [url]

    site = _get_link_type(post)
    if site == GFYCAT:
        try:
            return gfycat.get_media_from_post(post)
        except Exception as e:
            logging.error(f"Encountered error while extracting media links from URL: {str(url)}. Post ID: {post.id}"
                          f"Error Traceback:\n{traceback.format_exc()}")
            return []
    elif site == REDGIFS:
        try:
            return redgifs.get_media_from_post(post)
        except Exception as e:
            logging.error(f"Encountered error while extracting media links from URL: {str(url)}. Post ID: {post.id}"
                          f"Error Traceback:\n{traceback.format_exc()}")
            return []
    elif site == IMGUR:
        try:
            return imgur.get_media_from_post(post)
        except Exception as e:
            logging.error(f"Encountered error while extracting media links from URL: {str(url)}. Post ID: {post.id}"
                          f"Error Traceback:\n{traceback.format_exc()}")

            # Imgur link is removed, mark as such
            if e.status_code == 404 and remove_saved:
                logging.warning("Imgur link is removed, removing post from saved")
                post.unsave()

            return []
    elif site == VREDDIT:
        try:
            return [post.media['reddit_video']['fallback_url']]
        except Exception as e:
            logging.error(f"Encountered error while extracting media links from URL: {str(url)}. Post ID: {post.id}"
                          f"Error Traceback:\n{traceback.format_exc()}")
            return []
    elif site == INSTAGRAM:
        try:
            return instagram.get_media_from_post(post)
        except Exception as e:
            logging.error(f"Encountered error while extracting media links from URL: {str(url)}. Post ID: {post.id}"
                          f"Error Traceback:\n{traceback.format_exc()}")
            return []
    elif site == RGALLERY:
        try:
            return reddit_gallery.get_media_from_post(post)
        except Exception as e:
            logging.error(f"Encountered error while extracting media links from URL: {str(url)}. Post ID: {post.id}"
                          f"Error Traceback:\n{traceback.format_exc()}")
            return []
    else:
        # Link not supported, ignore and remove from saved
        if post.removal_reason is not None and remove_saved:
            logging.warning(f"Post ID {post.id} was removed, removing from saved list")
            post.unsave()
        return []


def _get_link_type(post):
    """Abstracts the mapping of post's URL to a supported domain"""
    url = post.url
    domain = '{uri.netloc}'.format(uri=urlparse(url)).replace("www.", "")
    if domain == "gfycat.com":
        return GFYCAT
    elif domain == "redgifs.com":
        return REDGIFS
    elif domain == "imgur.com":
        return IMGUR
    elif domain == "v.redd.it":
        return VREDDIT
    elif domain == "instagram.com":
        return INSTAGRAM
    elif domain == "reddit.com" and post.is_gallery:
        return RGALLERY
    elif enable_ytdl:
        # Try to download using youtube-dl
        return YTDL
    else:
        # Otherwise, don't support the link
        logging.warning(f"Encountered unsupported link during parsing: {str(url)}. Post ID: {post.id}")
        return "unknown"


def _is_direct_media_link(url):
    """Determines if the given link is a direct link to supported media"""
    ext = path.splitext(path.basename(urlparse(url).path))[1]
    return ext in accepted_extensions
