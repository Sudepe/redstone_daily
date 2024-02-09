import time, json, crawler
from bilibili_api import search, sync, video as bilivideo, credential
from tqdm import tqdm

def is_video_compliant(title, description, tags):
    # 处理标题数据
    flag = False
    tmp_string = ''
    for i in title:
        if i == '<':
            flag = True
        if flag:
            if i == '>':
                flag = False
            continue
        tmp_string += i
    title = tmp_string

    # 创建一个权重,用于分析视频数据
    weight = 1
    # 判断是否包含关键字,如果包含则权重变化
    terms = [
        "红石火把", "红石线", "红石中继器", "红石比较器", "逻辑门", "二进制", "全加器", "减法器",
        "红石时钟", "脉冲发生器", "单稳态", "双稳态", "T触发器", "RS触发器", "D触发器", "计数器",
        "分频器", "解码器", "编码器", "多路复用器", "红石计算机",
        "自动农场", "捕鱼机", "刷怪塔", "经验农场", "红石矿车", "自动熔炉", "物品分类", "自动门",
        "隐藏门", "红石电梯", "水流控制", "岩浆流控制", "自动化养鸡", "骨粉自动施", "村民交易",
        "红石存储器", "红石锁存器", "寄存器", "移位寄存器", "随机存取", "只读存储器", "可编程逻辑", "红石硬盘",
        "TNT炮", "飞沙炮", "水流炮", "凋零炮", "自动填装", "连发机构", "瞄准系统", "红石炮塔",
        "防御系统",
        "模拟信号", "信号强度", "衰减器", "增强器", "红石压力", "测重压力", "模拟时钟", "模拟传感",
        "音量控制", "红石调光",
        "活塞", "粘性活塞", "机械臂", "红石机械", "自动门机", "隐藏楼梯", "红石飞行", "红石车辆",
        "红石船", "飞行器控制"]

    weight_map = [
        {'keyword': '服务器', 'weight': 0},
        {'keyword': '游戏实况', 'weight': 0},
        {'keyword': '实况', 'weight': 0},
        {'keyword': '机械动力', 'weight': 0},
        {'keyword': '模组', 'weight': 0},
        {'keyword': 'MOD', 'weight': 0},
        {'keyword': '生存', 'weight': 0.3},
        {'keyword': '生电', 'weight': 1.5},
        {'keyword': '数电', 'weight': 1.5},
        {'keyword': '模电', 'weight': 1.5},
        {'keyword': '械电', 'weight': 1.5},
        {'keyword': '储电', 'weight': 1.5},
        {'keyword': '炮电', 'weight': 1.5},
        {'keyword': '音乐', 'weight': 0},
        {'keyword': '红石电路', 'weight': 2},
        {'keyword': '红石科技', 'weight': 2},
        {'keyword': '沙雕红石', 'weight': 2},
        {'keyword': '求助', 'weight': 0},
        {'keyword': '光遇', 'weight': 0},# 这个词纯属无奈,我真的会谢
    ]
    for i in weight_map:
        if i['keyword'] in title:
            weight *= i['weight']
        if i['keyword'] in description:
            weight *= i['weight']
        if i['keyword'] in tags:
            weight *= i['weight']
    for i in terms:
        if i in title:
            weight *= 1.5
        if i in description:
            weight *= 1.5
        if i in tags:
            weight *= 1.5
    if '红石' not in title:
        weight *= 0.6
    if '红石' not in description:
        weight *= 0.6
    if '红石' not in tags:
        weight *= 0.6
    if '红石' in tags:
        weight *= 1.37
    return weight


# 计算视频综合得分
def calc_score(like, view, favorite, coin, share):
    return view + like * 3 + favorite * 4 + coin * 10 + share * 4


def get_today_video(credential_obj):
    # 初始化计数器
    i = 0
    print('程序已启动,开始搜索视频')
    time_1 = time.time()

    # 使用crawler模块搜索并获取今日视频列表
    video_list = crawler.search_video()

    time_2 = time.time()
    print('搜索已完成,共搜索到',len(video_list),'个视频,耗时',time_2 - time_1,'秒,开始筛选视频')

    # 检查视频列表是否为空，如果为空则输出提示信息，并返回'NO_VIDEO'
    if len(video_list) == 0:
        print('今天居然没有视频 ERR_CODE=NO_VIDEO')
        return 'NO_VIDEO'

    # 创建临时变量存储符合规则的视频列表
    temp_video_list = []

    # 遍历所有视频，过滤出符合规则的视频并添加到临时列表中
    for video in tqdm(video_list):
        i += 1
        weight = is_video_compliant(video['title'], video['description'], video['tag'])
        if weight > 0.5:
            temp_video_list.append([video,weight])

    # 将符合规则的视频列表赋值给原视频列表
    video_list = temp_video_list

    time_3 = time.time()
    print('筛选已完成,共筛选到',len(video_list),'个视频,耗时',time_3 - time_2,'秒,开始处理视频')

    # 检查经过筛选后的视频列表是否为空，如果为空则输出提示信息，并返回'NOT_FOUND'
    if len(video_list) == 0:
        print('今天居然没有符合规则的视频 ERR_CODE=NOT_FOUND')
        return 'NOT_FOUND'

    # 初始化结果列表用于存放处理后的视频信息
    result_list = []

    # 遍历符合规则的视频列表，获取每个视频的各项详细信息
    for video in tqdm(video_list):
        # 创建bilivideo.Video对象并获取其详细信息
        video_obj = bilivideo.Video(bvid=video[0]["bvid"], credential=credential_obj)
        res = sync(video_obj.get_info())
        # 获取视频字幕信息
        conclude = sync(video_obj.get_ai_conclusion(res['cid']))

        title = video[0]['title']  # 视频标题
        description = video[0]['description']  # 视频描述
        author = video[0]['author']  # 视频作者
        url = video[0]['arcurl']  # 视频链接
        cover_url = video[0]['pic']  # 视频封面链接
        upic = video[0]['upic']  # UP主头像链接
        play = video[0]['play']  # 视频播放次数
        review = video[0]['review']  # 视频评论数量
        like = video[0]['like']  # 视频点赞数
        coin = res['stat']['coin']  # 视频投币数
        share = res['stat']['share']  # 视频分享数
        favorite = video[0]['favorites']  # 视频收藏数
        pubdate = res['pubdate'] # 视频发布时间
        danmaku = res['stat']['danmaku'] # 视频弹幕数
        score = calc_score(like, play, favorite, coin, share) # 视频综合得分
        weight = video[1]

        result_list.append({
            'title': title,
            'description': description,
            'author': author,
            'url': url,
            'cover_url': cover_url,
            'upic': upic,
            'play': play,
            'review': review,
            'like': like,
            'coin': coin,
            'share': share,
            'favorite': favorite,
            'pubdate': pubdate,
            'danmaku': danmaku,
            'score': score,
            'conclusion': conclude,
            'weight': weight
        })# 将视频信息添加到结果列表中

        # 为了避免频繁请求，暂停3秒后再处理下一个视频
        time.sleep(3)
    # 返回处理完成的视频信息列表
    time_4 = time.time()
    print('处理已完成耗时',time_4 - time_3,'秒,开始排序')
    return result_list
# 对视频依据self['weight']进行排序
def sort_video(video_info_list):
    # 从大到小排序,使用冒泡排序
    time_1 = time.time()
    for i in range(len(video_info_list)):
        for j in range(len(video_info_list) - 1):
            if video_info_list[j]['weight'] < video_info_list[j + 1]['weight']:
                video_info_list[j], video_info_list[j + 1] = video_info_list[j + 1], video_info_list[j]
    time_2 = time.time()
    print('排序已完成,耗时',time_2 - time_1,'秒,开始写入文件')
    return video_info_list

# 将视频信息写入文件
def write_video_info(video_info_list):
    time_1 = time.time()
    # 创建文件字典
    dict = {
        "title" : time.strftime("%Y-%m-%d", time.localtime()),
        "description" : "阿巴阿巴",
        "content" : []}
    for i in tqdm(video_info_list):
        dict['content'].append(
            {
                "type": "video",
                "title": i['title'],
                "description": i['description'],
                "url": i['url'],
                "cover_url": i['cover_url'],
                "pubdate": i['pubdate'],
                "data": {
                    "play": i['play'],
                    "review": i['review'],
                    "like": i['like'],
                    "coin": i['coin'],
                    "share": i['share'],
                    "favorite": i['favorite'],
                    "danmaku": i['danmaku'],
                    "score": i['score']
                },
                "author": {
                    "name": i['author'],
                    "upic": i['upic']
                }
            }
        )
    # 将文件字典写入Json文件
    filename = './data/database/' + time.strftime("%Y-%m-%d", time.localtime()) + '.json'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dict, ensure_ascii=False, indent=4))

    time_2 = time.time()
    print('写入文件已完成,耗时',time_2 - time_1,'秒')