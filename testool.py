from bot import x
from bot.story import Story

if __name__ == '__main__':
    story = Story()
    tweets_subjects, tweets_others = story.now_class()

    # 输出拆分后的推文
    for tweet in tweets_subjects:
        print(tweet)
        print("------------")
    for tweet in tweets_others:
        print(tweet)
        print("------------")

    # 测试推送
    bot = x.Bot()

    # 示例推文内容

    # 认证 Twitter API
    api = bot.authenticate_twitter()

    # 发送连发推文
    bot.send_tweets(api, tweets_subjects + tweets_others)
