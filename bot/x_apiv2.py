import os

from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session


class Tweets:
    def __init__(self):
        load_dotenv()
        self.consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        self.consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        self.TWEET_MAX_LENGTH = 280  # TWEET Max Length

    def split_tweets(self, content):
        """
        将长推文分割为不超过 280 个字符的多个推文。
        """
        tweets = []
        current_tweet = ""

        for line in content.split("\n"):
            # 如果整行文字超出最大长度，进一步拆分行
            while len(line) > self.TWEET_MAX_LENGTH:
                # 取出一段最大长度的字符作为推文
                tweets.append(line[:self.TWEET_MAX_LENGTH])
                # 将剩余部分继续处理
                line = line[self.TWEET_MAX_LENGTH:]

            # 处理剩余部分
            if len(current_tweet) + len(line) + 1 > self.TWEET_MAX_LENGTH:
                tweets.append(current_tweet.strip())
                current_tweet = line + "\n"
            else:
                current_tweet += line + "\n"

        if current_tweet.strip():
            tweets.append(current_tweet.strip())

        return tweets

    def post(self, payload: dict):
        """
        :param payload: See https://developer.x.com/en/docs/x-api/tweets/manage-tweets/api-reference/post-tweets
        :return:
        """

        # Make the request
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
        )

        # Making the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        return response

    @staticmethod
    def auto_post(text):
        """
        自動ポスト組み立て
        :return:
        """
        tweets = Tweets()
        for_send = tweets.split_tweets(text)

        sent_posts_data = []
        last_round = None
        for k in range(len(for_send)):
            # ポストを組み立て
            media = {}
            content = {
                "text": for_send[k]
            }
            if last_round is not None:
                response = last_round.json()
                content["reply"] = {"in_reply_to_tweet_id": response["data"]["id"]}

            last_round = tweets.post(
                content
            )
            sent_posts_data.append(last_round)

        return sent_posts_data


if __name__ == '__main__':
    tweets = Tweets()
    tweets.auto_post("""This is an example of a long tweet that will be automatically split into multiple tweets 
    if it exceeds Twitter's 280 character limit. This is useful for sending threads on Twitter.
    Each tweet will reply to the previous one, forming a tweet thread.This is an example of a long tweet that will be automatically split into multiple tweets 
    if it exceeds Twitter's 280 character limit. This is useful for sending threads on Twitter.
    Each tweet will reply to the previous one, forming a tweet thread.""")
