import logging

from dynamo_handler import add_article, is_in_db
from line_handler import format_message, send_line
from scraping import get_pr

# ログの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# ロガーの作成
logger = logging.getLogger(__name__)

# ブラックリストの文字列 LINE通知したくない内容を入力してください。
blacklist_words = ["メディア関係者", "PayPay" "メルカード", "マツケンサンバ"]


def is_in_blacklist(title):
    for black_word in blacklist_words:
        if black_word in title:
            return True
    return False


# Lambdaのエントリーポイント
def lambda_handler(event, context):
    """
    company_id_listには、company_idを入力してください。
    company_idとは、PRTIMESの記事URLの".html"の直前の数字のことです。
    URL例:"https://prtimes.jp/main/html/rd/p/000000333.000129774.html"
    このURLの場合は、129774です。
    0埋めはあってもなくても正常に動作します。
    """
    company_id_list = [129774, 13971, 25121, 26386]
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
