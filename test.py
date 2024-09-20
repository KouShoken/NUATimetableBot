import requests
import json

# Replace with your Bearer Token
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAALaGvwEAAAAAs77rVkiLSyv%2BbpkVP26TIgMDXDk%3DUy6PxUQqAOZ1x0UJN7RMHCMhf9rMHW5MAWuvQfL3O9JWIvwgvm'

# URL for posting a tweet
url = "https://api.twitter.com/2/tweets"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Function to send a tweet
def send_tweet(tweet_text, in_reply_to_tweet_id=None):
    payload = {
        "text": tweet_text
    }
    if in_reply_to_tweet_id:
        payload["reply"] = {"in_reply_to_tweet_id": in_reply_to_tweet_id}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f"Tweet sent successfully: {tweet_text}")
        return response.json()['data']['id']
    else:
        print(f"Failed to send tweet: {response.status_code} - {response.text}")
        return None

# Example tweet chain
tweets = [
    "This is the first tweet in the chain.",
    "This is the second tweet, replying to the first.",
    "This is the third tweet, continuing the chain."
]

# Send the first tweet
first_tweet_id = send_tweet(tweets[0])

# Send the rest of the tweets as replies
if first_tweet_id:
    reply_to_id = first_tweet_id
    for tweet in tweets[1:]:
        reply_to_id = send_tweet(tweet, reply_to_id)
