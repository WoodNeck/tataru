from cogs.utils.http_handler import HTTPHandler


def test_youtube_url():
    urls = ["https://www.youtube.com/playlist?list=", "https://www.youtube.com/playlist?list=426"]
    http = HTTPHandler()