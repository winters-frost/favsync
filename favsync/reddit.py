import praw
import traceback
import logging


# Gets a list of links to scrape.
#
# Gets a list of links from the user's saved submissions, while
# logging and keeping track of what has already been scraped.
def get_saved_list(user_auth, force_all=False, limit=None):
    reddit = praw.Reddit(client_id=user_auth["client_id"], client_secret=user_auth["client_secret"],
                         username=user_auth["username"], password=user_auth["password"],
                         user_agent=user_auth["user_agent"])

    saved_list = []
    reddit_saved = reddit.user.me().saved(limit=limit)
    for saved in reddit_saved:
        try:
            if type(saved) == praw.models.Submission:  # or type(saved) == praw.models.Comment:
                # TODO only scrape from last timestamp (or something)
                # if <check timestamp> or force_all:
                saved_list.append(saved)
        except Exception as e:
            # Log failure
            logging.error(traceback.format_exc())
            pass
    return saved_list


def get_post_type(post):
    if type(post) == praw.models.Submission:
        return "submission"
    elif type(post) == praw.models.Comment:
        return "comment"
    else:
        return "unknown"


def get_hosted_media_link(post):
    return post
