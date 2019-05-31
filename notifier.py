import praw
import re


def main():
    reddit = praw.Reddit('notifier', user_agent="reddit-manga-notifier")
    manga_stream = reddit.subreddit('manga').stream
    pattern = re.compile(
        '^(?:\\[[Dd][Ii][Ss][Cc]\\] ?)?'                    
        '(?P<Title>.+?)'
        '(?: ?\\(?|[ :\\|•-]*| ?[Vv]ol\\..*?)'
        '(?:[Cc]h(?:\\.?|apter)) ?'
        '(?P<Chapter>\\d+\\.?\\d*).*')

    for submission in manga_stream.submissions():
        if is_manga(submission):
            # ignore manga oneshots and other manga which doesn't follow the pattern
            match = pattern.search(submission.title)
            if match:
                print(match.groups())


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
