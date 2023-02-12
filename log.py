import logging

# init logging
logger = logging.getLogger()
fh = logging.FileHandler('adttp.log', encoding='utf-8', mode='a')
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)-8s : %(lineno)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.INFO)
