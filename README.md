# add-deepdanbooru-tags-to-photoprism

使用[DeepDanbooru](https://github.com/KichangKim/DeepDanbooru)提取[PhotoPrism](https://github.com/photoprism/photoprism)图像的 tags ，并写入到「Label/标签」/保存到本地

## Install

1. 下载源码，并放到`/app`目录下

2. 配置环境
    ```shell
    conda install --yes --file /app/add-deepdanbooru-tags-to-photoprism/requirements.txt -n base
    conda activate base
    pip install tensorflow_io
    ```
3. 定时任务执行`python create_labels.py`

### 模型

如果仅识别动漫图像且无其他需求，可以直接下载[预训练模型](https://github.com/KichangKim/DeepDanbooru/releases)，然后将文件解压放至`/app/add-deepdanbooru-tags-to-photoprism/`，然后修改`get_model_and_tags()`中模型路径

### 挂载目录

将 PhotoPrism 的图片目录同样挂载到此项目的`/app/`目录下

### 修改配置

在正式使用前，需要修改以下配置：

1. `create_labels.py`中 photoprism 的配置信息
    ```python
    api = photoprism.Client(
        domain='http://localhost:2342',
        username='admin',
        password='adminadmin',
        debug=False
    )
    ```

2. photoprism 偏移量，用于统计哪些新图片需要处理。第一次使用请改为 0
    ```shell
    echo -n '0'>photo_offset.txt
    ```

3. 执行分析前让 photoprism 索引目录。如有多个目录，则需要添加多个此命令
    ```python
    api.index_photos('/TwitterFavoritesArchive')
    ```

## Use cases

![](example.jpg)

## TODO

- [ ] 将识别出来的人物添加到 PhotoPrism
- [ ] 将识别出来的 rating 与 PhotoPrism 的「私有」结合
- [ ] Danbooru 标签中文化
- [ ] 并发处理

## 目录结构

```
├─deepdanbooru # DeepDanbooru源码，请至原项目获取最新源码
├─deepdanbooru-v3-20211112-sgd-e28 # DeepDanbooru预训练模型，请至原项目获取最新模型
├─photoprism # photoprism-python-sdk源码，略有修改，请至原项目获取最新源码
├─tag_score # 按UID.txt保存标签与分数
```

## Thanks

本项目缝合内容来自以下优秀项目，在此表示感谢

- [KichangKim/DeepDanbooru](https://github.com/KichangKim/DeepDanbooru)
- [dominikholler/photoprism-python-sdk](https://github.com/dominikholler/photoprism-python-sdk)
- [rachmadaniHaryono&Bewinxed](https://github.com/KichangKim/DeepDanbooru/issues/56#issuecomment-1100770505)