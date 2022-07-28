from nonebot import on_notice, on_command, permission, CommandGroup, get_bot
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent
import os
import json
from PIL import Image, ImageDraw, ImageFont
import random
import base64
from io import BytesIO

pic_gen = on_command("pic_gen", aliases={"邀请函"})

resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
font_file = os.path.join(resource_dir, 'font.ttf')
template_file = os.path.join(resource_dir, 'template.jpg')

def img_to_b64(pic: Image.Image) -> str:
    buf = BytesIO()
    pic.save(buf, format="PNG")
    base64_str = base64.b64encode(buf.getbuffer()).decode()
    return "base64://" + base64_str

async def make_jpg(text: str) -> Image.Image:
    template = Image.open(template_file)
    font = ImageFont.truetype(font_file, size=30)
    draw = ImageDraw.Draw(template)
    #居中显示文字
    text1 = "欢迎"
    text2 = text
    text3 = "加入网络安全协会"
    


    text_width1 = draw.textsize(text1, font=font)[0]
    text_width2 = draw.textsize(text2, font=font)[0]
    text_width3 = draw.textsize(text3, font=font)[0]

    draw.text(((template.width - text_width1) / 2, 0+700), text1, font=font, fill=(255, 255, 255))
    draw.text(((template.width - text_width2) / 2, 50+700), text2, font=font, fill=(237, 202, 202))
    draw.text(((template.width - text_width3) / 2, 100+700), text3, font=font, fill=(255, 255, 255))
    # draw.text((100, 750), text, font=font, fill=(255, 255, 255))
    # save the image to a file
    randomFilename = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 8)) + '.jpg'
    savePath = os.path.join(resource_dir, randomFilename)
    template.save(savePath)
    return savePath

@pic_gen.handle()
async def _pic_gen_handle(bot: Bot, event: Event, state: T_State):
    args = event.message.extract_plain_text().split(' ')
    if len(args) == 1:
        await bot.send(event, "请输入邀请函内容")
        return
    text = ' '.join(args[1:])
    title = '{}'.format(text)
    pic =await make_jpg(title)
    
    await bot.send(event, MessageSegment.image(img_to_b64(Image.open(pic))))
    os.remove(pic)
    return True