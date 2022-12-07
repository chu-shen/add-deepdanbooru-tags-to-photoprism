#!/usr/bin/env python3
"""
Source code: https://github.com/dominikholler/photoprism-python-sdk/blob/main/examples/create_labels_by_tags.py
"""
import photoprism
import os
from tqdm import tqdm
from get_tags import get_tags_and_score, get_model_and_tags

api = photoprism.Client(
    domain='http://192.168.3.8:2342',
    username='admin',
    password='adminadmin',
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


def process_photo_labels(photo, model, tags):
    """
    获得图片存储位置并计算标签
    """
    photo_uid = photo['UID']
    print("Processing file: ", photo_uid)
    # 文件存在则跳过
    if not os.path.exists(f'./tag_score/{photo_uid}.txt'):
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
            print("WARN:load name from FileName failed")
        if filename:
            filePath = os.path.join("/app", filename)
            tag_sets = get_tags_and_score(filePath, model, tags)

            # TODO 修改逻辑
            save_to_file = True
            # 大批量建议设为 false，通过 shell 脚本导入。小批量/日常使用设为 true
            direct_add_to_photoprism = True
            try:
                if tag_sets:
                    if direct_add_to_photoprism and not save_to_file:
                        for tag, score in tag_sets:
                            add_label_to_photoprism(
                                photo['UID'], tag, int((1-score)*100))
                    elif save_to_file and not direct_add_to_photoprism:
                        with open(f'./tag_score/{photo_uid}.txt', 'w') as f:
                            for tag, score in tag_sets:
                                f.write(f"{tag},{score}\n")
                    else:
                        with open(f'./tag_score/{photo_uid}.txt', 'w') as f:
                            for tag, score in tag_sets:
                                f.write(f"{tag},{score}\n")
                                add_label_to_photoprism(
                                    photo['UID'], tag, int((1-score)*100))
            except:
                print("Failed to add labels: ", photo_uid)
    else:
        print("File already processed: ", photo_uid)

def process_photos(model, tags):
    """
    处理 photoprism 中所有 offset 之后新增图片
    """
    total_offset = len(api.get_photos())

    with open('./photo_offset.txt', 'r') as f:
        old_offset = f.read()

    try:
        # 需处理的图片总数
        photos_num = total_offset-int(old_offset)
    except:
        photos_num = total_offset
    print("photos_num: ", photos_num)
    # 仅获取新增的图片
    new_photos = api.get_photos(
        order='added',
        count=photos_num,
        offset=0
    )

    for photo in tqdm(new_photos):
        process_photo_labels(photo, model, tags)

    with open('./photo_offset.txt', 'w') as f:
        f.write(str(total_offset))
        print("Finish write new offset!")


def process_one_photo(model, tags):
    """
    根据提供的单个 photoprism UID 处理对应图片
    """
    photo = api.get_photo('PRLYQ5E33UG64BPI')
    print(photo.items())
    process_photo_labels(photo, model, tags)


if __name__ == '__main__':
    # 索引图片目录
    api.index_photos('/TwitterFavoritesArchive')
    model, tags = get_model_and_tags()
    process_photos(model, tags)
    # process_one_photo(model, tags)
