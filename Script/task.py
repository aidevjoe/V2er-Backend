import feedparser
import sqlite3
import time
import jpush
from jpush import common
from threading import Timer
import config
import io
import sys
import os 

_jpush = jpush.JPush(config.app_key, config.master_secret)
#_jpush.set_logging("DEBUG")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def pushForAlias(id, msg, link):
    push = _jpush.create_push()
    alias=[id]
    alias1={"alias": alias}
    push.audience = jpush.audience(
        alias1
    )

    ios = jpush.ios(alert=msg, sound="default", extras={'link': link})
    push.notification = jpush.notification(alert="Hello world with audience!", ios=ios)
    push.options = {"time_to_live":86400, "sendno":12345,"apns_production": config.is_release}
    push.platform = "ios"
    print(push.payload)
    # push.send()
    try:
        response=push.send()
    except common.Unauthorized:
        raise common.Unauthorized("Unauthorized")
    except common.APIConnectionException:
        raise common.APIConnectionException("conn")
    except common.JPushFailure:
        print("JPushFailure")
    except:
        print("Exception")


def connectDB():
    # 上级目录
    currnetDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dbPath = currnetDir + '/v2er.db'
    connect = sqlite3.connect(dbPath)

    cursor = connect.cursor()

    cursor.execute('select * from User where isOnline = 1')
    values = cursor.fetchall()

    for value in values:
        name = value[1]
        lastMsgTime = value[2]
        feedURL = value[3]

        print("--------", name, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "--------")
        print("Feed URL = ", feedURL)

        d = feedparser.parse(feedURL)
    
        if len(d.entries) == 0:
           continue

        # 取出第一条消息
        entrie = d.entries[0]
        title = entrie.title
        content = entrie.content[0].value
        published = time.mktime(entrie.updated_parsed)

        link = entrie.link
        print(link)
        print("最新消息时间戳: ", published)
        print("本地最后一条消息时间戳: ", lastMsgTime)
        print("标题: ", title)
    
        if lastMsgTime is not None and published > lastMsgTime:
            pushForAlias(name, title, link)
        
        cursor.execute("update user set lastMsgTime = ? where name = ?", (published, name))
        print("--------", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "--------")

    cursor.close()

    connect.commit()
    connect.close()

connectDB()
