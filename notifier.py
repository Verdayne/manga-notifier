import praw
import re


def main():
    reddit = praw.Reddit('notifier', user_agent="reddit-manga-notifier")
    manga_stream = reddit.subreddit('manga').stream
    pattern = [
        # Covers most of the post
        re.compile(
            '^(?:\\[[Dd][Ii][Ss][Cc]\\] ?)?'                    
            '(?P<Title>.+?)'
            '(?: ?\\(?|[ :\\|•-]*| ?[Vv]ol\\..*?)'
            '(?:[Cc]h(?:\\.?|apter)) ?'
            '(?P<Chapter>\\d+\\.?\\d*).*'),

        # Covers outlier
        re.compile(
            '^(?:\\[[Dd][Ii][Ss][Cc]\\] ?)?'
            '(?:[Cc]h(?:\\.?|apter)) ?'
            '(?P<Chapter>\\d+\\.?\\d*) '
            '(?P<Title>.+)')
    ]

    for submission in manga_stream.submissions():
        if is_manga(submission):
            # ignore manga oneshots and other manga which doesn't follow the pattern
            match = pattern[0].search(submission.title)
            if match is None:
                continue

            title, chapter = match.groups()

            if title.isspace():
                match = pattern[1].search(submission.title)
                title = match.group('Title')

            print('{} {}'.format(title, chapter))


def is_manga(submission):
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


if __name__ == '__main__':
    main()
