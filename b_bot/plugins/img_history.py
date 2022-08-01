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

img_history = on_command("img_history", aliases={"图片历史"})

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
