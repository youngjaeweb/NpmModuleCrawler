# coding:utf8
import logging
import sqlite3
import pymysql

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(filename)s[%(lineno)s] - %(message)s')

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

logger.addHandler(sh)


def sqlite_connect():
    return sqlite3.connect('K:/Study/python/PackageScrap/src/npm.sqlite')


def mysql_connect():
    return pymysql.connect(host='',
                           user='',
                           password='@!',
                           db='npm_module_schema',
                           charset='utf8mb4')


def get_npm_modules():
    conn = mysql_connect()
    with conn.cursor() as c:
        c.execute("SELECT COUNT(*) FROM MODULE")

        db_module_cnt = c.fetchone()

    with sqlite_connect() as conn:
        c = conn.cursor()

        c.execute("""
            SELECT A.NAME, B.VERSION, A.LICENSE, A.LATEST_VER, A.STABLE_VER, B.SHASUM, B.TABALL_URL, A.DESCRIPTION
              FROM MODULE_INFO A, MODULE_RELEASES B
             WHERE A.ID = B.MODULE_ID
               AND B.ROWID > ?
        """, db_module_cnt)
        return (row for row in c.fetchall())


if __name__ == '__main__':
    conn = mysql_connect()
    with conn.cursor() as c:
        logger.debug('Start Action!!')
        try:
            for row in get_npm_modules():
                c.execute("""
                  INSERT INTO MODULE (NAME, VER, LICENSE, LATEST_VER, STABLE_VER, SHASUM, TABALL_URL, DESCRIPTION)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                    str(row[7]).encode('utf8').decode('utf-8')))
            logger.debug('Success!!')
        except Exception as e:
            logger.error(e)
            logger.error('Insert Error (%s, %s)' % (row[0], row[1]))
            logger.error('Description %s' % (str(row[7]).encode('utf8').decode('utf-8')))
        finally:
            conn.commit()
            logger.debug('Commit Action!!')
