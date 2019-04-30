# twitter-purge
Python 2 program that deletes your tweets and unfaves your favorites older than X days. Requires [tweepy](https://www.tweepy.org/).

If there are any of your tweets you want to save, edit the `SAVED_TWEET_IDS` array in the `main.py` script.

Usage: `CONSUMER_TOKEN=<consumer token> CONSUMER_SECRET=<consumer secret> python main.py --days 30`
