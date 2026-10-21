import argparse
import json
import re
import sys

import boto3
from botocore.exceptions import BotoCoreError, ClientError

SOURCE_BUCKET = "data-fellow-crawler-project"
TARGET_BUCKET = "data-fellow-athena-news"
REGION = "eu-north-1"

DEFAULT_KEY = "news/sports/2026/10/20/00-06.json"

PATTERN = re.compile(
    r"^news/([^/]+)/(\d{4})/(\d{2})/(\d{2})/([^/]+)\.json$"
)


def transform(s3, key, execute=False):

    match = PATTERN.fullmatch(key)

    if not match:
        return ("skip", 0, f"Desteklenmeyen dosya yolu: {key}")

    category, year, month, day, filename = match.groups()

    # Yeni bucket'taki dosyanın yolu
    destination = (
        f"news/category={category}/"
        f"year={year}/month={month}/day={day}/"
        f"{filename}.jsonl"
    )

    # Eski JSON dosyasını S3'ten oku
    response = s3.get_object(
        Bucket=SOURCE_BUCKET,
        Key=key
    )

    records = json.loads(
        response["Body"].read().decode("utf-8-sig")
    )

    if not isinstance(records, list):
        raise ValueError(f"JSON dizisi bulunamadı: {key}")

    if not records:
        return ("skip", 0, f"Boş JSON dosyası: {key}")

    lines = []

    # Haberleri tek tek JSONL satırına dönüştür
    for index, item in enumerate(records):

        if not isinstance(item, dict):
            raise ValueError(
                f"Geçersiz haber: {key}, sıra: {index}"
            )

        if item.get("category") != category:
            raise ValueError(
                f"Kategori uyuşmazlığı: {key}, sıra: {index}"
            )

        out = dict(item)

        # Kategori bilgisi artık klasör yolundan okunacak
        out.pop("category", None)

        lines.append(
            json.dumps(
                out,
                ensure_ascii=False,
                separators=(",", ":")
            )
        )

    output_bytes = (
        "\n".join(lines) + "\n"
    ).encode("utf-8")

    if execute:

        try:
            s3.head_object(
                Bucket=TARGET_BUCKET,
                Key=destination
            )

            return ("exists", len(records), destination)

        except ClientError as exc:
            if exc.response["Error"]["Code"] not in (
                "404", "NoSuchKey", "NotFound"
            ):
                raise

        s3.put_object(
            Bucket=TARGET_BUCKET,
            Key=destination,
            Body=output_bytes,
            ContentType="application/x-ndjson"
        )

        head = s3.head_object(
            Bucket=TARGET_BUCKET,
            Key=destination
        )

        if head["ContentLength"] != len(output_bytes):
            raise RuntimeError(
                f"Dosya boyutu uyuşmuyor: {destination}"
            )

    return (
        "written" if execute else "preview",
        len(records),
        destination
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--all",
        action="store_true",
        help="Bütün eski JSON dosyalarını işle"
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Yeni bucket'a dosyaları yaz"
    )

    parser.add_argument(
        "--key",
        default=DEFAULT_KEY,
        help="Test edilecek JSON dosyası"
    )

    parser.add_argument(
        "--profile",
        help="AWS CLI profil adı"
    )

    args = parser.parse_args()

    session = boto3.Session(
        profile_name=args.profile,
        region_name=REGION
    )

    s3 = session.client("s3")
    sts = session.client("sts")

    print("AWS Account:", sts.get_caller_identity()["Account"])
    print("Region:", REGION)
    print("Kaynak:", SOURCE_BUCKET)
    print("Hedef:", TARGET_BUCKET)

    print(
        "Mod:",
        "ALL" if args.all else "ONE",
        "WRITE" if args.execute else "DRY RUN"
    )

    keys = []

    if args.all:

        paginator = s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(
            Bucket=SOURCE_BUCKET,
            Prefix="news/"
        ):

            keys.extend(
                obj["Key"]
                for obj in page.get("Contents", [])
                if obj["Key"].endswith(".json")
            )

    else:
        keys = [args.key]

    stats = {
        "preview": 0,
        "written": 0,
        "exists": 0,
        "skip": 0,
        "failed": 0
    }

    articles = 0

    for i, key in enumerate(keys, 1):

        try:
            status, count, info = transform(
                s3, key, args.execute
            )

            stats[status] += 1
            articles += count

            print(
                f"[{i}/{len(keys)}] {status.upper()}: "
                f"{key} -> {info} ({count} haber)"
            )

        except (
            ValueError,
            ClientError,
            BotoCoreError,
            json.JSONDecodeError,
            RuntimeError
        ) as exc:

            stats["failed"] += 1

            print(
                f"[{i}/{len(keys)}] FAILED: {key} -> {exc}",
                file=sys.stderr
            )

    print("Özet:", stats)
    print("Toplam görülen haber:", articles)

    if stats["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
