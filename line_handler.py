import logging
import os

import pyshorteners
import requests

# ロガーの作成
logger = logging.getLogger(__name__)


# LINEの通知を行う関数
def send_line(message):
    LINE_TOKEN = os.environ["LINE_TOKEN"]
    # LINE_TOKEN = ""
    api_url = "https://notify-api.line.me/api/notify"
    send_contents = "\n" + message
    TOKEN_dic = {"Authorization": "Bearer " + LINE_TOKEN}
    send_dic = {"message": send_contents}

    response = requests.post(api_url, headers=TOKEN_dic, data=send_dic)

    if response.status_code == 200:
        logger.info("Message sent successfully")
    else:
        logger.info("Failed to send message")


# urlを短縮する関数
def generate_shortened_url(long_url):
    try:
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(long_url)
        return short_url
    except Exception as e:
        logger.info(f"Error generating shortened URL: {e}")
        return long_url


# メッセージのフォーマットを整える関数
def format_message(title, url):
    short_url = generate_shortened_url(url)
    if len(title) > 50:
        # タイトルが50文字以上の場合は短縮
        short_title = title[:47] + "..."
        message = f"{short_title}\n{short_url}\n"
    else:
        message = f"{title}\n{short_url}\n"
    return message
