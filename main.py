from bilibili_api import search, sync, video as bilivideo, credential
import time, json, requests, crawler, generator, asyncio, sys
from tqdm import tqdm
with open('credential.txt', 'r') as f:
    text = f.read().split('\n')
credential = credential.Credential(text[0],text[1])
time_1 = time.time()
videos = generator.get_today_video(credential)
generator.write_video_info(generator.sort_video(videos))
time_2 = time.time()
print('程序已结束,耗时',time_2 - time_1,'秒')