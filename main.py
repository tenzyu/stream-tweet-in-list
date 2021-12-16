from threading import Timer

import requests
import tweepy

import constant
from modules.twitter import Twitter


def post(message):
    requests.post(constant.WEBHOOK_URL, {"content": message})


class Stream(tweepy.Stream):
    def on_request_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            post("<@608242236546613259> Twitter API rate limit exceeded.")
            return False

    def on_status(self, status):
        if (
            status.is_quote_status
            or status.in_reply_to_user_id
            or hasattr(status, "retweeted_status")
            or "RT @" in status.text
            or "media" not in status.entities
        ):
            return

        post(f"https://twitter.com/{status.user.screen_name}/status/{status.id}")


class MiiTweet:
    def __init__(self) -> None:
        self.api = Twitter(*constant.TWITTER_CREDENTIALS)
        self.stream = Stream(*constant.TWITTER_CREDENTIALS)
        self.list_id = constant.WATCH_LIST_ID
        self.member_ids = self.get_list_member_ids()

    def get_list_member_ids(self) -> set[int]:
        count = self.api.get_list(list_id=self.list_id).member_count
        members = self.api.get_list_members(list_id=self.list_id, count=count)
        return set(map(lambda member: member.id, members))

    def update_list_status(self) -> bool:
        print("called update_list_status")
        new_member_ids = self.get_list_member_ids()
        if new_member_ids != self.member_ids:
            self.member_ids = new_member_ids
            return True
        return False

    def run(self):
        Timer(60, self.run).start()

        if self.stream.running:
            if self.update_list_status():
                post("リストの更新を検知したため再接続します。再接続には最大2分かかります。")
                self.stream.disconnect()
                post("切断しました。")
        else:
            post("接続します。")
            self.stream.filter(follow=self.member_ids)


if __name__ == "__main__":
    mii_tweet = MiiTweet()
    mii_tweet.run()
