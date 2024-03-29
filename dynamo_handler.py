import logging

import boto3

# ロガーの作成
logger = logging.getLogger(__name__)


# DBに記事の送信記録が存在するか確認する関数
def is_in_db(url, company_id):
    # DynamoDBクライアントを初期化
    dynamodb = boto3.client("dynamodb")
    table_name = "Articles"

    try:
        # テーブルが存在するか確認
        response = dynamodb.describe_table(TableName=table_name)
        logger.info("responded by dynamodb")
    except dynamodb.exceptions.ResourceNotFoundException:
        # テーブルが存在しない場合は新規作成
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "company_id", "KeyType": "HASH"}, {"AttributeName": "url", "KeyType": "RANGE"}],
            AttributeDefinitions=[{"AttributeName": "company_id", "AttributeType": "N"}, {"AttributeName": "url", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # テーブルが存在しない場合 = 過去に一度も送ったことがない = Trueを返す = 送信処理はしない
        return True

    # 記事の存在を確認
    try:
        response = dynamodb.get_item(
            TableName=table_name, Key={"company_id": {"N": str(company_id)}, "url": {"S": url}}, ProjectionExpression="title"
        )
        # 記事が存在する場合はTrueを返す=送信処理はしない
        if "Item" in response:
            logger.info("article does not exist")
            return True
        # 記事が存在しない場合はFalseを返す=送信する
        else:
            logger.info("article exists")
            return False

    except Exception as e:
        logger.info(f"Error checking item: {e}")
        return True


# 記事をテーブルに追加する関数
def add_article(title, url, company_id):
    dynamodb = boto3.client("dynamodb")
    table_name = "Articles"

    # item作成
    item = {
        "company_id": {"N": str(company_id)},
        "url": {"S": url},
        "title": {"S": title},
    }

    # 追加
    try:
        dynamodb.put_item(TableName=table_name, Item=item)
        logger.info("Item added successfully")
    except Exception as e:
        logger.info(f"Error adding item: {e}")
