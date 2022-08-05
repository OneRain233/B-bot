from distutils.command.upload import upload
from nonebot import on_notice, on_command, permission, CommandGroup
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent
import os
import json
from .pic_gen import img_to_b64
from PIL import Image, ImageDraw, ImageFont
import random
import requests

img_history = on_command("img_history", aliases={"我要看黑历史","黑历史"})
upload_img = on_command("upload_img", aliases={"上传图片"})

# resources/img/
resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'img')

def get_random_img():
    filelist = os.listdir(resource_dir)
    return random.choice(filelist)

@img_history.handle()
async def img_handle(bot: Bot, event: Event, state:T_State):
    img = get_random_img()
    img_file = os.path.join(resource_dir, img)
    img = Image.open(img_file)
    await bot.send(event, MessageSegment.image(img_to_b64(img)))

async def download_img(url):
    try:
        r = requests.get(url)
        # save to resources/img/
        filename = str(random.randint(0, 1000000)) + '.png'
        filepath = os.path.join(resource_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        return filename
    except Exception as e:
        print(e)
        return False

def get_imgs(msg):
    imgs = []
    for m in msg:
        try:
            seg: MessageSegment = m
            if seg.data['url']:
                imgs.append(seg.data['url'])
        except:
            pass
    return imgs

@upload_img.handle()
async def upload_img_handle(bot: Bot, event: Event, state:T_State):
    try:
        msg = event.get_message()
        msg_seg: MessageSegment = msg[1]
        # img_url = msg_seg.data['url']
        img_url = get_imgs(msg)
        if len(img_url) == 0:
            await bot.send(event, '没有图片')
        for i in img_url:
            filename = await download_img(i)
            if filename:
                await bot.send(event, MessageSegment.image(img_to_b64(Image.open(os.path.join(resource_dir, filename)))))
                await bot.send(event, '图片上传成功')
        
    except Exception as e:
        await bot.send(event, "上传失败 {}".format(e))

