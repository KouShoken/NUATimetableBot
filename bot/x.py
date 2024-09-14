import os
import tweepy

from dotenv import load_dotenv

load_dotenv()


class Bot:
    def __init__(self):
        # 从环境变量中获取 Twitter API v2 的凭证
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret_key = os.getenv('TWITTER_API_SECRET_KEY')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.TWEET_MAX_LENGTH = 280  # Twitter 单条推文字符限制

    # 使用 Twitter API v2 的 Client 进行身份验证
    def authenticate_twitter(self):
        client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret_key,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )
        return client

    # 分割推文
    def split_tweets(self, content):
        """
        将长推文分割为不超过 280 个字符的多个推文。
        """
        tweets = []
        current_tweet = ""

        for line in content.split("\n"):
            if len(current_tweet) + len(line) + 1 > self.TWEET_MAX_LENGTH:
                tweets.append(current_tweet.strip())
                current_tweet = line + "\n"
            else:
                current_tweet += line + "\n"

        if current_tweet.strip():
            tweets.append(current_tweet.strip())

        return tweets

    # 使用 Twitter API v2 发送连发推文
    def send_tweets(self, client, tweet_list):
        reply_to_tweet_id = None
        for tweet in tweet_list:
            if reply_to_tweet_id:
                # 使用 Twitter API v2 发布推文，并回复之前的推文
                new_tweet = client.create_tweet(text=tweet, in_reply_to_tweet_id=reply_to_tweet_id)
            else:
                # 发布第一条推文
                new_tweet = client.create_tweet(text=tweet)

            # 获取新推文的 ID 用于连发
            reply_to_tweet_id = new_tweet.data['id']

        print(f"Sent {len(tweet_list)} tweets.")


# 示例主函数
if __name__ == '__main__':
    bot = Bot()

    # 示例推文内容
    tweet_content = """
    This is an example of a long tweet that will be automatically split into multiple tweets 
    if it exceeds Twitter's 280 character limit. This is useful for sending threads on Twitter.
    """

    # 认证 Twitter API
    api = bot.authenticate_twitter()

    # 分割推文
    tweet_list = bot.split_tweets(tweet_content)

    # 发送连发推文
    bot.send_tweets(api, tweet_list)
