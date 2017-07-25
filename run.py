# coding:utf8
from npm.npm_crawler import crawl_registry, set_target_dir

import configparser
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(filename)s[%(lineno)s] - %(message)s')

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

logger.addHandler(sh)

c = configparser.ConfigParser()

with open('config.cfg') as f:
    config = f.read()
    logger.debug(c.read_string(config))

    set_target_dir(c.get('DOWNLOAD', 'TARGET_DIR'))
    module_list_loc = c.get('DOWNLOAD', 'MODULE_LIST_LOC')

if __name__ == '__main__':
    """NPM 모듈 크롤러
    """

    with open(module_list_loc, 'r') as f:
        for value in f.readlines():
            arr = value.strip().split('==')
            name = arr[0]
            ver = arr[1] if len(arr) == 2 else None
            crawl_registry(name, ver)
