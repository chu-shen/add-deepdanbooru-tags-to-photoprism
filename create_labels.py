#!/usr/bin/env python3
"""
Source code: https://github.com/dominikholler/photoprism-python-sdk/blob/main/examples/create_labels_by_tags.py
"""
import photoprism
import os
import sys
from get_tags import get_tags_and_score, get_model_and_tags
import sqlite3
import pickle
from config import *
import concurrent.futures
from log import logger


api = photoprism.Client(
    domain=PHOTOPRISM_URL,
    username=PHOTOPRISM_USERNAME,
    password=PHOTOPRISM_PASSWORD,
    debug=False
)


def add_label_to_photoprism(uid, name, uncertainty):
    """
    more label info:
    https://github.com/photoprism/photoprism/blob/develop/internal/classify/label.go
    https://github.com/photoprism/photoprism/blob/develop/internal/entity/label.go
    https://github.com/photoprism/photoprism/blob/develop/internal/api/photo_label.go
    """
    api.add_label_to_photo(
        photo_uid=uid,
        label_name=name,
        label_uncertainty=uncertainty
    )


def process_photo_labels(conn, cursor, photo, model, tags):
    """
    获得图片存储位置并计算标签
    """
    photo_uid = photo['UID']
    # Check if the tweet is already in the database
    cursor.execute(
        "SELECT * FROM deepdanbooru_results_of_photoprism WHERE photoprism_id=?", (photo_uid,))
    if cursor.fetchone():
        return

    # 获取图片存储位置
    filename = ''
    try:
        # 单图且非sidecar
        if 'FileName' in photo and photo['FileRoot'] != 'sidecar':
            filename = photo['FileName']
        elif photo['Files'] != None:
            # 堆叠图片只取非sidecar及video
            for file in photo['Files']:
                if file['Root'] == 'sidecar' or file['MediaType'] == 'video':
                    continue
                else:
                    filename = file['Name']
    except:
        logger.warn("load name from FileName failed")
        return

    tags_scores = {}

    # 迁移旧数据至数据库
    # TODO: to be removed in the future
    if os.path.exists(f'./tag_score/{photo_uid}.txt'):
        with open(f'./tag_score/{photo_uid}.txt') as f:
            for line in f:
                tag, score = line.strip().split(",")
                tags_scores[tag] = float(score)
        cursor.execute("INSERT INTO deepdanbooru_results_of_photoprism VALUES (?,?, ?, ?)",
                       (photo_uid, filename, sqlite3.Binary(pickle.dumps(tags_scores)), 1))
        conn.commit()
        return

    if filename:
        filePath = os.path.join(FILE_PATH, filename)
        tag_sets = get_tags_and_score(filePath, model, tags)
        try:
            if tag_sets:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_to_tag = {executor.submit(add_label_to_photoprism, photo_uid, tag, int(
                        (1-score)*100)): (tag, score) for tag, score in tag_sets}
                    for future in concurrent.futures.as_completed(future_to_tag):
                        tag, score = future_to_tag[future]
                        try:
                            tags_scores[tag] = score
                        except Exception as exc:
                            logger.error(
                                f'{tag} generated an exception: {exc}')
                cursor.execute("INSERT INTO deepdanbooru_results_of_photoprism VALUES (?,?, ?, ?)",
                               (photo_uid, filename, sqlite3.Binary(pickle.dumps(tags_scores)), 1))
        except KeyboardInterrupt:
            logger.warn("Interrupted by user")
            sys.exit()
    else:
        cursor.execute("INSERT INTO deepdanbooru_results_of_photoprism VALUES (?,?, ?, ?)",
                       (photo_uid, photo['FileName'], sqlite3.Binary(pickle.dumps(tags_scores)), 0))
    conn.commit()


def process_photos(model, tags):
    """
    处理 photoprism 中所有 offset 之后新增图片
    """
    # Connect to the SQLite database
    conn = sqlite3.connect("deepdanbooru_results_of_photoprism.db")
    cursor = conn.cursor()

    # Create the table to store the data if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deepdanbooru_results_of_photoprism (
            photoprism_id TEXT PRIMARY KEY,
            photo_name TEXT,
            deepdanbooru_results BLOB,
            is_succeed BOOLEAN
        )
        """)

    # 需处理的图片总数
    # TODO 优化处理数
    total_offset = len(api.get_photos())
    photos_num = total_offset

    new_photos = api.get_photos(
        order='added',
        count=photos_num,
        offset=0
    )

    try:
        for photo in new_photos:
            process_photo_labels(conn, cursor, photo, model, tags)
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit()

    conn.close()


def process_one_photo(model, tags):
    """
    根据提供的单个 photoprism UID 处理对应图片
    """
    photo = api.get_photo('PRLYQ5E33UG64BPI')
    print(photo.items())
    process_photo_labels(photo, model, tags)


if __name__ == '__main__':
    # 索引图片目录
    api.index_photos(INDEX_PATH)
    model, tags = get_model_and_tags()
    process_photos(model, tags)
    # process_one_photo(model, tags)
