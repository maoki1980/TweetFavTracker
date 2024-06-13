import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        screen_name = request.form["screen_name"]
        return redirect(url_for("main.likes", screen_name=screen_name, page=1))

    return render_template("index.html")


@main.route("/likes/<screen_name>/<int:page>", methods=["GET"])
def likes(screen_name, page):
    url = "https://api.x.com/1.1/favorites/list.json"
    params = {
        "count": 10,
        "screen_name": screen_name,
        "page": page,
    }  # 1ページあたりのツイート数を10に変更
    headers = {
        "authorization": f"Bearer {current_app.config['BEARER_TOKEN']}",
        "content-type": "application/json",
        "cookie": f"auth_token={current_app.config['AUTH_TOKEN']}; ct0={current_app.config['CT0']};",
        "x-csrf-token": current_app.config["CT0"],
        "Host": "api.x.com",
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        likes_list = response.json()

        # 各ツイートに対して埋め込みHTMLを取得
        for tweet in likes_list:
            tweet_url = f"https://twitter.com/{tweet['user']['screen_name']}/status/{tweet['id_str']}"
            tweet["embed_html"] = get_oembed_html(tweet_url)

        return render_template(
            "likes.html", likes_list=likes_list, screen_name=screen_name, page=page
        )
    else:
        flash(f"Error: {response.status_code}")
        return redirect(url_for("main.index"))


def get_oembed_html(tweet_url):
    oembed_params = {
        "url": tweet_url,
        "hide_thread": "true",
        "omit_script": "true",
        "align": "center",
        "lang": "ja",
    }
    oembed_url = "https://publish.twitter.com/oembed"
    oembed_response = requests.get(oembed_url, params=oembed_params)
    if oembed_response.status_code == 200:
        oembed_data = oembed_response.json()
        return oembed_data["html"].strip()
    else:
        return ""
