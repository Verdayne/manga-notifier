import praw
import re
from typing import NamedTuple


class Manga(NamedTuple):
    """ Represent a manga"""
    name: str
    chapter: int
    url: str


def init_reddit_stream():
    reddit = praw.Reddit('notifier', user_agent="manga-notifier")
    return reddit.subreddit('manga').stream


def init_regex():
    """Cleaner means of compiling regex needed for this script

    :return: returns an array of compiled regex
    """
    pattern = [
        # covers majority
        re.compile(r'^(?:\[disc\] ?)?(?P<name>.+?)(?: ?\(?|[ :|•-]*| ?vol\..*?)'
                   r'(?:ch(?:\.?|apter)) ?(?P<chapter>\d+\.?\d*).*', re.IGNORECASE),

        # Covers outlier
        re.compile(r'^(?:\[disc\] ?)?(?:ch(?:\.?|apter)) ?'
                   r'(?P<chapter>\d+\.?\d*) (?P<name>.+)', re.IGNORECASE)
    ]
    return pattern


def likely_manga(submission) -> bool:
    """Check /r/ submission for likelihood of being a manga

    :param submission: a reddit post
    :return: if post is likely to be manga
    """
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


def regex_get_match(title: str, patterns):
    """Gets the regex that matches.

    Majority of submissions are (name) then (chapter),
    however, I have seen a few submissions where the (chapter)
    precedes (name). This function is to handle said the outliers

    :param title: the post's title being searched
    :param patterns: the array of regex used to search
    :return: regex.match if found or None
    """

    for pattern in patterns:
        match = pattern.match(title)
        if match:
            # if the (name) is only space, the title format is reversed
            if not match.group('name').isspace():
                return match
    return None


def get_manga(submission, patterns):
    """Returns a Manga obj if submission is a manga, else None


    :param submission: a reddit post
    :param patterns: the array of regex used to search
    :return: Manga obj or None
    """
    if not likely_manga(submission):
        return None

    match = regex_get_match(submission.title, patterns)

    if match is None:
        return None

    # Has to separate groups because title can be both first and last in groups
    # This is needed because /r/manga doesn't have a submission standard
    title = match.group('name')
    chapter = match.group('chapter')
    return Manga(title, chapter, submission.url)


class RedditManga:
    def __init__(self):
        """Initialize a RedditManga instance.
        """
        self._regex = init_regex()
        self._stream = init_reddit_stream()

    def get(self) -> Manga:
        """Get a stream of manga from /r/manga
        :rtype: Manga
        """

        for submission in self._stream.submissions():
            if submission is None:
                continue

            manga_obj: Manga = get_manga(submission, self._regex)
            if manga_obj is None:
                continue

            yield manga_obj


if __name__ == '__main__':
    rmc = RedditManga()

    for manga in rmc.get():
        print(manga)
