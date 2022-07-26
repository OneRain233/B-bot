from nonebot import on_command, on_startswith
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
from .txt2img import txt2img
from nonebot.adapters.onebot.v11 import MessageSegment
from .pic_gen import img_to_b64

drama = on_command('drama', aliases={'新番', '番'}, priority=5)
@drama.handle()

async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    res = await get_data()
    img = txt2img(res).save()
    msg = MessageSegment.image(img_to_b64(img))
    await drama.send(msg)
    
    # return "\n".join(msglist)\

async def get_data():
    import json
    import requests
    import datetime

    api = "https://bangumi.bilibili.com/web_api/timeline_global"
    date=datetime.datetime.now()
    m=str(date.month)
    d=str(date.day)
    dt=str(date.day+1)
    today =m+"-"+d
    tomorrow = m+"-"+dt
    print(m+"-"+d)  
    msglist = []
    req = requests.get(api)
    resp = req.json()
    for a in resp['result']:
        # print(a['date'])
        if a['date'] == today:
            msglist.append(a['date'])
            for b in a['seasons']:
                # print(b['pub_time'],b['title'],b['pub_index'])
                temp = b['pub_time']+" "+b['title']+" "+b['pub_index']
                msglist.append(temp)
        elif a['date'] == tomorrow:
            msglist.append(a['date'])
            for b in a['seasons']:
                # print(b['pub_time'],b['title'],b['pub_index'])
                temp = b['pub_time']+" "+b['title']+" "+b['pub_index']
                msglist.append(temp)
    res = '\n'.join(msglist)
    
    return res