import os
import sys
import tweepy
import json
import webbrowser
from datetime import datetime, timedelta

DEFAULT_THRESHOLD = 30 # days
SAVED_TWEET_IDS = []

consumer_token = os.environ['CONSUMER_TOKEN']
consumer_secret = os.environ['CONSUMER_SECRET']
auth = tweepy.OAuthHandler(consumer_token, consumer_secret)

def do_auth():
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print('Error! Failed to get request token.')
        raise
    webbrowser.open_new_tab(redirect_url)
    verifier = input('Verifier:')
    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')
        raise
    creds = {
        'access_token': auth.access_token,
        'access_token_secret': auth.access_token_secret
    }
    # Store key and secret for further use
    with open('auth.json','w') as f:
        f.write(json.dumps(creds))
    return creds

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            resume_time = datetime.now() + timedelta(minutes=15)
            print('[!] Hit rate limit error. Waiting 15 minutes until {}.'.format(resume_time))
            time.sleep(15 * 60) # 15 minutes

def main():
    threshold = DEFAULT_THRESHOLD
    if sys.argv[1] == '-d' or sys.argv[1] == '--days':
        threshold = int(sys.argv[2])
    now = datetime.now()
    try:
        with open('auth.json','r') as f:
            creds = json.loads(f.read())
    except FileNotFoundError:
        creds = do_auth()
    auth.set_access_token(creds['access_token'], creds['access_token_secret'])
    api = tweepy.API(auth)

    # Delete tweets older than threshold days
    print("### Deleting tweets older than {} days old ###".format(threshold))
    for status in limit_handled(tweepy.Cursor(api.user_timeline).items()):
        if status.created_at + timedelta(days=threshold) < now:
            # skip saved tweets
            if status.id in SAVED_TWEET_IDS:
                print('Skipping tweet ID {} created at {} (saved tweet): {}'.format(status.id, status.created_at, status.text.encode('utf-8')))
            else:
                print('Deleting tweet ID {} created at {}: {}'.format(status.id, status.created_at, status.text.encode('utf-8')))
                api.destroy_status(status.id)
        else:
            print('Skipping tweet ID {} created at {} (too new): {}'.format(status.id, status.created_at, status.text.encode('utf-8')))

    # Unfav tweets older than threshold days
    print("\n\n### Deleting favorites for tweets older than {} days old ###".format(threshold))
    for fav in limit_handled(tweepy.Cursor(api.favorites).items()):
        if fav.created_at + timedelta(days=threshold) < now:
            print('Unfavoriting tweet ID {} created at {}: {}'.format(fav.id, fav.created_at, fav.text.encode('utf-8')))
            api.destroy_favorite(fav.id)
        else:
            print('Skipping fav of tweet ID {} created at {} (too new): {}'.format(fav.id, fav.created_at, fav.text.encode('utf-8')))

if __name__ == '__main__':
    main()
