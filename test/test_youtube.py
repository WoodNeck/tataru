from cogs.google import Google


def test_youtube_url():
    cog = Google(None)
    not_okay_ids = ["", 426, 0, "SomeNotValidUrl"]
    for listId in not_okay_ids:
        videos = cog.searchVideoList(listId)
        assert(len(videos) == 0)
    good_ids = ["LLxhtmDROwDNmTIPPBARYW4A", "UUxhtmDROwDNmTIPPBARYW4A"]
    for listId in good_ids:
        videos = cog.searchVideoList(listId)
        assert(len(videos) != 0)
