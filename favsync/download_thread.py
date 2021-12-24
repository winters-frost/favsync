import os
import threading
import traceback
import logging
import requests
import re
from urllib.parse import urlparse
import youtube_dl


class DownloadThread(threading.Thread):
    def __init__(self, queue, target_dir, options):
        super(DownloadThread, self).__init__()
        self.queue = queue
        self.target_dir = target_dir
        self.options = options
        self.daemon = True
        self.successCounter = 0

        # Options for youtube-dl
        self.ydl_opts = {
            'format': 'best',
            'quiet': True,
            'outtmpl': os.path.join(target_dir, "%(title)s.%(ext)s")
        }

    def run(self):
        logging.debug("DownloadThread spawned [ThreadID " + str(self.ident) + "]")

        while True:
            entry = self.queue.get()
            try:
                self.download_entry(entry)
            except Exception as e:
                logging.error(f"[ThreadID {str(self.ident)}] Encountered catastrophic failure during download_entry(): "
                              f"{str(e)}\n{traceback.format_exc()}")
            self.cleanup()
            self.queue.task_done()

    def download_entry(self, entry):
        # Loop through all the links scanned for the post
        for i in range(len(entry["links"])):
            url = entry["links"][i]
            filename = self.get_filename(url)
            if filename is None:
                continue

            dest_filename = f"{entry['post']}-{i}{os.path.splitext(filename)[1]}"

            path = os.path.join(self.target_dir, dest_filename)
            if os.path.exists(path):
                # File already exists
                logging.warning(f"[ThreadID {str(self.ident)}] {dest_filename} already exists, skipping... (URL: {str(url)})")
                if self.options.remove_saved and not self.options.dry_run:
                    entry["post"].unsave()
                continue

            # Download the file
            if self.options.dry_run:
                logging.info(f"[ThreadID {str(self.ident)}] Skipping download: {filename} (URL: {str(url)})")
                if not self.options.silent:
                    print(f"[ThreadID {str(self.ident)}] Skipping download: {filename} (URL: {str(url)})")
            else:
                logging.debug(f"[ThreadID {str(self.ident)}] Attempting to download {filename} (URL: {str(url)})")
                # If file is a CDN object, then download with youtube-dl
                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    with open(path, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                    self.successCounter += 1
                    logging.info(f"[ThreadID {str(self.ident)}] Successfully downloaded {filename} (URL: {str(url)})")

                    # Remove from saved if specified
                    if self.options.remove_saved:
                        entry["post"].unsave()
                else:
                    logging.error(f"[ThreadID {str(self.ident)}] Failed to download {filename} (URL: {str(url)})")

    def get_filename(self, url):
        # Check if this URL needs any special handling to get the file name
        domain = '{uri.netloc}'.format(uri=urlparse(url)).replace("www.", "")

        try:
            if domain == "v.redd.it":
                # For these links, the name is the part before the DASH_*
                reg = re.compile(r'https?://v.redd.it/([A-z0-9]+)/DASH_[0-9]+')
                return reg.match(url)[1] + ".mp4"
            else:
                # Normally parse the name from the end of the URL
                return os.path.basename(urlparse(url).path)
        except Exception as e:
            logging.error(f"[ThreadID {str(self.ident)}] Failed to parse file name (URL: {str(url)}). Error received: "
                          f"{str(e)}")
            return None

    def download_cdn_media(self, url):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])

    def cleanup(self):
        logging.info(f"[ThreadID {str(self.ident)}] Cleaning up thread resources. Number files downloaded: "
                     f"{str(self.successCounter)}")
