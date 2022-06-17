#!/usr/bin/env python

import os
import sys
import configargparse
import atexit
import reddit
import const
from extractors import browser
from link_extractor import extract_media_links
import logging
from queue import Queue
from download_thread import DownloadThread


def favsync():
    options = parse_options()

    # Set up logging
    logging.basicConfig(filename=options.log_file, filemode="w", level=options.log_level,
                        format="[%(asctime)s - %(levelname)s] - %(message)s")

    # Validate options
    if options.num_threads < 1:
        print(f"Invalid number of threads specified: {options.num_threads}", file=sys.stderr)
        return
    if options.limit < 1:
        print(f"Invalid limit on number of posts specified: {options.limit}", file=sys.stderr)
        return

    # Validate target directory
    target_dir = os.path.abspath(options.output_dir)
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)

    # Build user auth dict
    user_auth = {
        "client_id": options.client_id,
        "client_secret": options.client_secret,
        "username": options.user,
        "password": options.password,
        "user_agent": options.user_agent
    }

    # Log the program entry point in the log
    logging.info("=========== favsync entry point ===========")

    # Get list of links to parse from reddit
    print("Querying saved posts...")
    saved = reddit.get_saved_list(user_auth, limit=options.limit)

    # Extract direct link to media from saved post
    print("Extracting links from posts...")
    media_links = extract_media_links(saved)

    # Begin downloading media
    print("Downloading files...")
    download_media_links(media_links, target_dir, options)

    # Handle any post-processing

    print("Finished")


def download_media_links(entries, target_dir, options):
    """Multi-threaded downloading of a list of links"""
    # Create task queue for the downloader threads
    queue = Queue()
    for entry in entries:
        queue.put(entry)

    for i in range(options.num_threads):
        t = DownloadThread(queue, target_dir, options)
        t.start()

    queue.join()


def parse_options():
    """Parses command line arguments, config file settings, and environment variables"""
    parser = configargparse.ArgParser(default_config_files=["/etc/favsync.conf", "~/.favsync"],
                                      description="Retrieves media files from a reddit account's saved posts")
    parser.add_argument("-d", "--output-dir", env_var="OUTPUT_DIR", required=True,
                        help="Directory to download media files to")
    parser.add_argument("-c", "--config", is_config_file=True, env_var="FAVSYNC_CONFIG", help="Config file path")
    parser.add_argument("--client-id", type=str, env_var="REDDIT_CLIENT_ID", required=True,
                        help="The reddit API client id")
    parser.add_argument("--client-secret", type=str, env_var="REDDIT_CLIENT_SECRET", required=True,
                        help="The reddit API client secret")
    parser.add_argument("--user", type=str, env_var="REDDIT_USER", required=True,
                        help="Reddit username to authenticate")
    parser.add_argument("--password", type=str, env_var="REDDIT_PASS", required=True, help="Reddit user password")
    parser.add_argument("--user-agent", type=str, default="favsync", env_var="USER_AGENT",
                        help="The user agent string to use while accessing the reddit API")
    parser.add_argument("--num-threads", type=int, default=4, env_var="NUM_THREADS",
                        help="The number of download threads to use")
    parser.add_argument("--hash-filenames", action="store_true",
                        help="Rename each file downloaded to the hash of its contents")  # TODO implement
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-s", "--silent", action="store_true", help="Enable silent mode")
    output_group.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging to stdout")  # TODO implement
    parser.add_argument("--log-file", type=str, default=const.DEFAULT_LOG_FILE, env_var="LOG_FILE",
                        help="Specify where to write log file")
    parser.add_argument("--log-level", type=str, default="WARNING", env_var="LOG_LEVEL",
                        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
                        help="Minimum severity of log level to log")
    parser.add_argument("--prefer-mp4", action="store_true", env_var="PREFER_MP4",
                        help="Prioritize mp4 files over other available formats")
    parser.add_argument("--limit", type=int, default=1024, env_var="LIMIT",
                        help="Limit the number of posts to retrieve")
    parser.add_argument("--remove-saved", action="store_true", env_var="REMOVE_SAVED",
                        help="Remove posts from saved once retrieved or if post media doesn't exist")
    parser.add_argument("--dry-run", action="store_true", env_var="DRY_RUN",
                        help="Run the tool without downloading any files")

    return parser.parse_args()


# Handle common exit tasks
@atexit.register
def close():
    browser.cleanup()
