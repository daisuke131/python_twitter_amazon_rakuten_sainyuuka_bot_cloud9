import os

import pandas as pd

from common.beutifulsoup import fetch_soup
from common.csv import write_csv
from common.tweet import Tweet

CSV_PATH = os.path.join(os.getcwd(), "csv/urls.csv")


class BuyableTweet:
    def __init__(self) -> None:
        self.df_list = []
        self.read_df = pd.read_csv(CSV_PATH)
        self.write_df = pd.DataFrame()

    def buy_tweet(self):
        tw = Tweet()
        for hash_tag, url, is_buyable in zip(
            self.read_df["ハッシュタグ"], self.read_df["URL"], self.read_df["前回購入可能か"]
        ):
            self.tweet_decision(hash_tag, url, int(is_buyable))

        for df_data in self.df_list:
            self.write_df = self.write_df.append(df_data, ignore_index=True)

    def tweet_decision(self, hash_tag: str, url: str, is_buyable: int):
        new_is_buyable = is_buyable
        soup = fetch_soup(url)
        if "amazon" in url:
            selector = "#add-to-cart-button"
            platform = "Amazon"
        elif "rakuten" in url:
            selector = "#normal_basket_11235153 > tbody > tr:nth-child(3) > td > span.floatingCartSplitButtons > span > span:nth-child(2) > button > span > span"
            platform = "楽天市場"
        else:
            return

        if soup.select(selector):
            if is_buyable == 0:
                formated_hash_tag = self.formating_hash_tag(hash_tag)
                title = soup.select("#productTitle")[0].get_text().replace("\n", "")
                # tw.tweet(f"＼{platform}で再入荷中／\n{title}\n{url}\n{formated_hash_tag}")
                print(f"＼{platform}で再入荷中／\n{title}\n{url}\n{formated_hash_tag}")
                new_is_buyable = 1
        else:
            if is_buyable == 1:
                new_is_buyable = 0

        self.df_list.append(
            {
                "ハッシュタグ": hash_tag,
                "URL": url,
                "前回購入可能か": new_is_buyable,
            }
        )

    def formating_hash_tag(self, hash_tag: str) -> str:
        hash_tag_list = hash_tag.split()
        new_hash_tag_list = []
        for s in hash_tag_list:
            new_hash_tag_list.append("#" + s)
        return " ".join(new_hash_tag_list)

    def write_csv(self):
        write_csv(CSV_PATH, self.write_df)


def main():
    bt = BuyableTweet()
    bt.buy_tweet()
    bt.write_csv()


if __name__ == "__main__":
    main()