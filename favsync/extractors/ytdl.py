import youtube_dl


def get_media_from_post(post):
    ydl_opts = {
        'format': 'best',
        'quiet': True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([post.url])
