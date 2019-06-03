import praw
import re
from typing import NamedTuple


class Manga(NamedTuple):
    """ Represent a manga"""
    title: str
    chapter: int
    url: str


def init_reddit_stream():
    reddit = praw.Reddit('notifier', user_agent="manga-notifier")
    return reddit.subreddit('manga').stream


def init_regex():
    pattern = [
        # covers majority
        re.compile(r'^(?:\[disc\] ?)?(?P<title>.+?)(?: ?\(?|[ :|•-]*| ?vol\..*?)'
                   r'(?:ch(?:\.?|apter)) ?(?P<chapter>\d+\.?\d*).*', re.IGNORECASE),

        # Covers outlier
        re.compile(r'^(?:\[disc\] ?)?(?:ch(?:\.?|apter)) ?'
                   r'(?P<Chapter>\d+\.?\d*) (?P<Title>.+)', re.IGNORECASE)
    ]
    return pattern


def is_discussion(submission) -> bool:
    # if submission lacks external link, skip
    if submission.is_self:
        return False

    # if submission has the wrong flair, skip
    flair = submission.link_flair_text
    if flair != 'DISC' and flair is not None:
        return False

    # check for rogue art links
    if submission.is_reddit_media_domain:
        return False

    # ignore releases in Japanese
    if 'RAW' in submission.title:
        return False

    return True


def regex_get_match(query: str, regexes):
    for regex in regexes:
        match = regex.match(query)
        if match:
            for group in match.groups():
                if not group.isspace():
                    return match
    return None


def valid_manga(submission, patterns):
    if not is_discussion(submission):
        return None

    match = regex_get_match(submission.title, patterns)

    if match is None:
        return None

    title = match.group('title')
    chapter = match.group('chapter')
    return Manga(title, chapter, submission.url)


class RedditManga:
    def __init__(self):
        self._regex = init_regex()
        self._stream = init_reddit_stream()

    def get_manga(self) -> Manga:
        """Get a stream of manga from /r/manga
        :rtype: Manga
        """
        for submission in self._stream.submissions():
            if submission is None:
                continue
            manga_obj: Manga = valid_manga(submission, self._regex)
            if manga_obj is None:
                continue

            yield manga_obj


if __name__ == '__main__':
    rmc = RedditManga()

    for manga in rmc.get_manga():
        print(manga)
