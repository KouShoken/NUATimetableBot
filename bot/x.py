import os
import tweepy
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


class Bot:
    def __init__(self):
        # 从环境变量中获取 Twitter API v1.1 的凭证
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret_key = os.getenv('TWITTER_API_SECRET_KEY')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.TWEET_MAX_LENGTH = 280  # Twitter 单条推文字符限制

    # 使用 Twitter API v1.1 进行身份验证
    def authenticate_twitter(self):
        auth = tweepy.OAuth1UserHandler(
            self.api_key, self.api_secret_key,
            self.access_token, self.access_token_secret
        )
        api = tweepy.API(auth)
        return api

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

    # 使用 Twitter API v1.1 发送连发推文
    def send_tweets(self, api, tweet_list):
        reply_to_tweet_id = None  # 记录上一条推文的 ID
        for tweet in tweet_list:
            if reply_to_tweet_id:
                # 使用 Twitter API v1.1 发布推文，并回复上一条推文
                new_tweet = api.update_status(status=tweet, in_reply_to_status_id=reply_to_tweet_id)
            else:
                # 发布第一条推文
                new_tweet = api.update_status(status=tweet)

            # 获取新推文的 ID，用于回复
            reply_to_tweet_id = new_tweet.id

        print(f"Sent {len(tweet_list)} tweets in a thread.")


# 示例主函数
if __name__ == '__main__':
    bot = Bot()

    # 示例推文内容（如果推文内容太长，会自动分割为多个推文）
    tweet_content = """
    This is an example of a long tweet that will be automatically split into multiple tweets 
    if it exceeds Twitter's 280 character limit. This is useful for sending threads on Twitter.
    Each tweet will reply to the previous one, forming a tweet thread.
    """

    # 认证 Twitter API
    api = bot.authenticate_twitter()

    # 分割推文
    tweet_list = bot.split_tweets(tweet_content)

    # 发送连发推文
    bot.send_tweets(api, tweet_list)
