from bilibili_api import search, sync
import time, sys

def search_from_bilibili(page = 1):
    # 搜索关键词
    keyword = "红石"
    # 搜索类型，这里指定为视频
    search_type = search.SearchObjectType.VIDEO
    # 排序类型，这里指定为综合排序
    order_type = search.OrderVideo.PUBDATE

    # 搜索函数
    async def search_videos():
        return await search.search_by_type(keyword, search_type=search_type, order_type=order_type, page=page)

    # 同步执行搜索函数
    res = sync(search_videos())

    # 过滤出最近1天的视频
    recent_videos = []
    targetTime = time.time() - 86400
    min = 86400
    for i in res['result']:
        interval = i['pubdate'] - targetTime
        if interval > 0:
            recent_videos.append(i)
            if min > interval:
                min = interval
    print(min)
    return recent_videos


def search_video():
    # 初始化标志位
    flag = True
    # 初始化计数器
    a = 0
    # 初始化搜索结果列表
    search_result=[]
    # 当标志位为真时循环执行以下操作
    while flag:
        # 计数器加一
        a += 1
        # 调用search_from_bilibili函数，传入计数器作为参数并获得结果
        result = search_from_bilibili(a)
        # 遍历结果列表
        for i in result:
            # 将每个元素添加到搜索结果列表中
            search_result.append(i)
        # 如果当前结果列表的长度小于20，则跳出循环
        print(len(result))
        if len(result) == 0:
            break
        # 打印搜索冷却中并等待30秒
        for i in range(5):
            message = '正在搜索...' + str(a) + '页','搜索冷却中... ' + str(5 - i) + 's'
            print(message)
            time.sleep(1)
    # 返回搜索结果列表
    return search_result

