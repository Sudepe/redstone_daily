from bilibili_api import search, sync, video as bilivideo, credential
import time, json, requests, crawler, generator, asyncio, sys
from tqdm import tqdm
credential = credential.Credential(
    "cfb948ba%2C1720814332%2C8820a%2A12CjD14fCf001Y8ZzNFNAFuABlOrfn0tD3zdJSzutm4gsPIZ-L-TUJAiZWzCe9w3LBJZISVm9oQUFSdFJBc21fVF8zX2hFRHRITGtjaEliUDJ3WmRlcEpycVprcVZDRjNrYVdUcjRySk41WTlHTHRCTHZudXExalJ1bGlPZ1pld0RkaHZzTXZqY21BIIEC",
    "46f4a304f3d9130649b5f32427f1c8f8")
time_1 = time.time()
videos = generator.get_today_video(credential)
generator.write_video_info(generator.sort_video(videos))
time_2 = time.time()
print('程序已结束,耗时',time_2 - time_1,'秒')