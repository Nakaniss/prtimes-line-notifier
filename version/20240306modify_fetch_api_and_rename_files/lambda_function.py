import logging

from dynamo_handler import add_article, is_in_db
from line_handler import format_message, send_line
from scraping import get_pr

# ログの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# ロガーの作成
logger = logging.getLogger(__name__)
# ログ出力例
# logger.info("This is main.")


# ブラックリストの文字列
blacklist_words = [
    "ウイスキー",
    "タコハイ",
    "セールスタート",
    "Coke ON",
    "チューハイ",
    "モルツ",
    "メディア関係者",
    "ビール",
    "ワイン",
    "アルコール",
    "ストロングゼロ",
    "お酒",
    "檸檬堂",
    "トリス",
    "ハイボール",
    "ほろよい",
    "山崎",
    "金麦",
    "白州",
    "知多",
    "天然水",
    "株式取得",
    "プロゴルファー",
    "文化財団",
    "サワー",
]


def is_in_blacklist(title):
    for black_word in blacklist_words:
        if black_word in title:
            return True
    return False


# Lambdaのエントリーポイント
def lambda_handler(event, context):
    company_id_list = [4158, 10896, 33194, 74056, 1735, 42435]
    for company_id in company_id_list:
        # 記事を取得する
        api_url = f"https://prtimes.jp/api/companies/{company_id}/press_releases?limit=5"
        pr_list = get_pr(api_url)
        logger.info(f"found {len(pr_list)} articles")
        for article in pr_list:
            title = str(article.title)
            url = str(article.url)
            logger.info(f"title:{title[:10]}...")
            logger.info(f"url:{url[:10]}...")

            # titleにブラックリストのワードが含まれていた場合は次の記事へ
            if is_in_blacklist(title):
                logger.info(f"{title[:10]}... exists in blacklist")
                continue

            # 既にDB内に存在している場合も次の記事へ
            if is_in_db(url, company_id):
                logger.info(f"{title[:10]}... already exists in db")
                continue

            # lineメッセージに記事のtitleとurlを追加する
            message = format_message(title, url)
            # LINEで通知する
            send_line(message)
            # DBに追加する
            add_article(title, url, company_id)

    return {
        "statusCode": 200,
    }
