import os
import pymysql
from email.utils import parsedate_to_datetime


def get_db_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        connect_timeout=10
    )


def parse_published_at(value):
    if not value:
        return None

    dt = parsedate_to_datetime(value)
    return dt.replace(tzinfo=None)


def save_articles(articles):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO news_articles (
                    category,
                    rank_no,
                    title,
                    description,
                    source,
                    published_at,
                    url,
                    scraped_at
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, UTC_TIMESTAMP()
                )
            """

            for article in articles:
                cursor.execute(
                    sql,
                    (
                        article["category"],
                        article["rank"],
                        article["title"],
                        article.get("description"),
                        article.get("source"),
                        parse_published_at(
                            article.get("published_at")
                        ),
                        article["url"]
                    )
                )

        connection.commit()

    finally:
        connection.close()