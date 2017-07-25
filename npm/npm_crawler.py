# coding:utf8
from __future__ import print_function
from urllib.request import urlopen, urlretrieve

from npm.db_sync import mysql_connect

import json
import logging
import sys
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(filename)s[%(lineno)s] - %(message)s')

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

logger.addHandler(sh)

target_dir = os.path.abspath(os.curdir)
target_dir = os.path.join(target_dir, 'download')
if not os.path.isdir(target_dir):
    os.mkdir(target_dir)

REGISTRY_URL = 'http://registry.npmjs.org/%s'

conn = mysql_connect()

target_dir = None


def set_target_dir(dir):
    global target_dir
    target_dir = dir


def create_module_dir(name, package):
    global target_dir

    if not target_dir:
        target_dir = os.path.join(os.path.abspath(os.pardir), 'module')

    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    module_dir = os.path.join(target_dir, name)
    if not os.path.isdir(module_dir):
        os.mkdir(module_dir)

    with open(os.path.join(module_dir, 'package.json'), 'w', encoding='utf8') as f:
        f.write(package)

    logger.debug('Module dir: %s' % module_dir)
    return module_dir


def mark_download_complete(name, version):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE MODULE
               SET DOWNLOAD = 1
             WHERE NAME = %s
               AND VER  = %s
        """, (name, version))
    conn.commit()


def already_download(name, version):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) AS CNT
              FROM MODULE
             WHERE NAME = %s
               AND VER  = %s
               AND DOWNLOAD = 1
        """, (name, version))

    return bool(cursor.fetchone()[0])


def crawl_registry(name, version=None):
    logger.error('module name: %s, version: %s' % (name, version))

    try:
        print(REGISTRY_URL % name)
        r = urlopen(REGISTRY_URL % name)
    except Exception as e:
        logger.error(e)
    else:
        package = r.read().decode('utf8')
        package_dict = json.loads(package)
        # logger.debug(package_dict)

        if not package_dict:
            logger.warning('Package information not found!! (%s)' % (name,))
            return

        try:
            version = version if version else package_dict.get('dist-tags').get('latest')
            module_dir = create_module_dir(name, package)

            r = urlopen(REGISTRY_URL % name + '/' + version)

            ver_json = r.read().decode('utf8')
            ver_dict = json.loads(ver_json)

            if not ver_dict:
                logger.warning('Package information not found!! (%s, %s)' % (name, version))

            real_ver = ver_dict['version']

            # 이미 파일이 받아져 있다면 받지 않도록 조치함
            if not already_download(name, real_ver):
                tarball_url = ver_dict['dist']['tarball']
                filename = tarball_url.split('/')[-1]
                logger.debug('Tarball url: %s, name: %s' % (tarball_url, filename))
                urlretrieve(tarball_url, os.path.join(module_dir, filename))
                mark_download_complete(name, real_ver)

                for k, v in ver_dict['dependencies'].items():
                    crawl_registry(k, v)
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    """NPM 모듈 크롤러

    버전 정보가 없을 경우 최신 버전을 가져온다.
    """
    param = sys.argv[1:]

    if len(param) < 1:
        logger.error('Parameter not found.')
        logger.error('Input format: python3 npm_crawler.py [module_name] :[version]')
        raise SystemExit

    module_name = param[0]
    module_ver = param[1] if len(param) == 2 else None

    logger.debug('module_name: %s, version: %s' % (module_name, module_ver))

    crawl_registry(module_name, module_ver)
