from reddit_manga import RedditManga


def main():
    reddit_manga = RedditManga()

    for manga in reddit_manga.get_manga():
        print(manga)


if __name__ == '__main__':
    main()
