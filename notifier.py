import praw


def main():
    reddit = praw.Reddit('notifier', user_agent="reddit-manga-notifier")
    manga_stream = reddit.subreddit('manga').stream

    for submission in manga_stream.submissions():
        print(submission.title)


if __name__ == '__main__':
    main()
