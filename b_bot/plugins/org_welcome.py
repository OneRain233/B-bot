from nonebot import on_command, on_startswith, on_notice
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import *
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from pathlib import Path

def img_to_b64(pic: Image.Image) -> str:
    buf = BytesIO()
    pic.save(buf, format="PNG")
    base64_str = base64.b64encode(buf.getbuffer()).decode()
    return "base64://" + base64_str


resource_dir = Path() / "data" / "resources"


# reply = on_command("?", aliases={"回复", "自动回复"}, priority=5)
# reply = on_keyword(keywords=['?', '？'], priority=5)
org_welcome = on_command("welcome", priority=5)
# 问卷
quiz = on_command("quiz", aliases={"问卷", "问卷调查"}, priority=1, block=False)

@org_welcome.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    # res = await get_data()
    # send img
    pic = os.path.join(str(resource_dir), 'post.jpg')
    
    img_url = "https://gchat.qpic.cn/gchatpic_new/2492994043/984900265-2928148383-A5707D9D1CC0E55BB6BFCFDACF13D5A4/0?term=255"
    # await org_welcome.send( MessageSegment.image(img_to_b64(Image.open(pic))))
    await org_welcome.send( MessageSegment.image(img_url))

@quiz.handle()
async def handle_quiz_receive(bot: Bot, event: Event, state: T_State):
    msg = "【腾讯文档】2022网络安全协会招新 https://docs.qq.com/form/page/DQU95T2h1dHR4VVFO"
    await quiz.send(msg)