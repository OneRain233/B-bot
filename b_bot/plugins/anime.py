from ast import alias
from typing import Awaitable
import feedparser
import time
from nonebot import on_command, on_startswith, on_notice
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
from mcstatus import JavaServer
from nonebot.rule import to_me
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Event, PokeNotifyEvent
from nonebot.adapters.onebot.v11 import MessageSegment
import os
from PIL import Image, ImageDraw, ImageFont
from .pic_gen import img_to_b64
import random
from .txt2img import *


anime_search = on_command('anime_search')
resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
zh_font_file = os.path.join(resource_dir, 'font.ttf')

async def search_data(key_word):
    url = "https://acg.rip/.xml?term={}".format(key_word)
    return await get_data(url)

async def get_data(rss_url):
    rss_ACG = feedparser.parse(rss_url)
    res = []
    li = rss_ACG.entries
    for i in li:
        # print(i['links'][0], i['links'][1])
        # print('\n')
        torrent_url = i['links'][1]['href']
        web_url = i['links'][0]['href']
        title = i['title']
        publish_time = i['published'] # 'Thu, 04 Aug 2022 07:38:10 -0700'
        publish_time = publish_time[:-6]
        # print(publish_time)
        res.append({'title': title, 'torrent_url': torrent_url, 'web_url': web_url, 'publish_time': publish_time})

    # print(res)
    return res

def format_list(l):
    res = []
    for i in l:
        s = "{} \n {} \n {} \n {} \n".format(i['title'], i['torrent_url'], i['web_url'], i['publish_time'])
        res.append(s)

    return "================================\n".join(res)

def str_2_img(s):
    # sl = s.split('\n')
    # font = ImageFont.truetype(zh_font_file, size=30)
    # w = font.getsize(s)[0]
    # h = font.getsize(s)[1]
    # new_img = Image.new('RGB', (w, h), (255, 255, 255))
    # draw = ImageDraw.Draw(new_img)
    # draw.text((0, 0), s, font=font, fill=(0, 0, 0))
    # randomFilename = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 8)) + '.jpg'
    # savePath = os.path.join(resource_dir, randomFilename)
    # new_img.save(savePath)
    # return img_to_b64(Image.open(savePath))
    font_size = 32
    title = 'Anime'
    text = s
    img = txt2img(text, "test.png",20, font_path=zh_font_file).save()
    # img = Txt2Img(font_size)
    # pic = img.save(title, text)
    msg = MessageSegment.image(img_to_b64(img))
    return msg
    

@anime_search.handle()
async def _anime_search(bot: Bot, event: Event, state: T_State):
    args = event.message.extract_plain_text().split(' ')
    if len(args) == 1:
        await bot.send(event, '请输入关键字')
        return
    await bot.send(event, '搜索中...{}'.format(args[1]))
    data = await search_data(args[1])
    msg123 = format_list(data)
    await bot.send(event, '搜索ok len:{}'.format(len(data)))
    try:
        await bot.send(event, msg123)
    except Exception as e:
        await bot.send(event, 'mht又不让我说话！！！正在转图片～')
        await bot.send(event, str_2_img(format_list(data)))