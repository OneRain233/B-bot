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

img_history = on_command("img_history", aliases={"图片历史"})
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

@upload_img.handle()
async def upload_img_handle(bot: Bot, event: Event, state:T_State):
    msg = event.get_message()
    msg_seg: MessageSegment = msg[1]
    img_url = msg_seg.data['url']
    filename = await download_img(img_url)
    if filename:
        img_url = "file://" + os.path.join(resource_dir, filename)
        await bot.send(event, MessageSegment.image(img_url))
    else:
        await bot.send(event, "上传失败")


