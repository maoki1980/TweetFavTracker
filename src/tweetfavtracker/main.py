import os

import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv("../../.env")

# 環境変数から認証情報を取得
auth_token = os.getenv("AUTH_TOKEN")
ct0 = os.getenv("CT0")
bearer_token = os.getenv("BEARER_TOKEN")
screen_name = os.getenv("SCREEN_NAME")

# Twitter APIのエンドポイントURL
favorites_url = "https://api.x.com/1.1/favorites/list.json"

# URLパラメータを設定
params = {"count": 20, "screen_name": screen_name}

# 認証情報とその他のヘッダーを設定
headers = {
    "authorization": f"Bearer {bearer_token}",
    "content-type": "application/json",
    "cookie": f"auth_token={auth_token}; ct0={ct0};",
    "x-csrf-token": ct0,
    "Host": "api.x.com",
}


def get_oembed_html(tweet_url):
    # oEmbed APIのパラメータを設定
    oembed_params = {
        "url": tweet_url,
        "hide_thread": "true",
        "omit_script": "true",
        "align": "center",
        "lang": "ja",
    }
    oembed_url = "https://publish.twitter.com/oembed"

    # oEmbed APIを使って埋め込みコードを取得
    oembed_response = requests.get(oembed_url, params=oembed_params)
    if oembed_response.status_code == 200:
        oembed_data = oembed_response.json()
        return oembed_data["html"].strip()
    else:
        print(
            f"Error fetching oEmbed data for tweet URL {tweet_url}: {oembed_response.status_code}"
        )
        return ""


# リクエストを送信して、いいねリストのレスポンスを取得
response = requests.get(favorites_url, headers=headers, params=params)

# レスポンスのステータスコードを確認
if response.status_code == 200:
    try:
        # レスポンスのJSONデータを取得
        likes_list = response.json()

        if likes_list:
            # HTMLファイルにツイートの埋め込みコードを保存
            with open("index.html", "w", encoding="utf-8") as file:
                file.write("<html><head>\n")
                file.write("<meta charset='UTF-8'>\n")
                file.write("""
                <script>
                window.twttr = (function(d, s, id) {
                  var js, fjs = d.getElementsByTagName(s)[0],
                    t = window.twttr || {};
                  if (d.getElementById(id)) return t;
                  js = d.createElement(s);
                  js.id = id;
                  js.src = "https://platform.twitter.com/widgets.js";
                  fjs.parentNode.insertBefore(js, fjs);

                  t._e = [];
                  t.ready = function(f) {
                    t._e.push(f);
                  };

                  return t;
                }(document, "script", "twitter-wjs"));
                </script>
                """)
                file.write("</head><body>\n")
                file.write("<h1>Liked Tweets</h1>\n")

                for tweet in likes_list:
                    tweet_id = tweet["id_str"]
                    tweet_url = f"https://twitter.com/{tweet['user']['screen_name']}/status/{tweet_id}"

                    # oEmbed APIから埋め込みHTMLを取得
                    embed_html = get_oembed_html(tweet_url)
                    file.write(embed_html + "\n")

                file.write("</body></html>\n")
        else:
            print("No likes found.")
    except ValueError:
        print("Error: Failed to decode JSON response")
else:
    print(f"Error: {response.status_code}")
    print("Response content:", response.text)
