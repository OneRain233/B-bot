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
import emoji
from pilmoji import Pilmoji
from pathlib import Path


pic_gen = on_command("pic_gen", aliases={"邀请函"})

# resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
resource_dir = Path() / "data" / "resources"
font_dir = Path() / "data" / "fonts"
# zh_font_file = os.path.join(resource_dir, 'font.ttf')
zh_font_file = font_dir / "font.ttf"
# emoji_font_file = os.path.join(resource_dir, 'consola.ttf')
template_file = resource_dir / "template.jpg"
logo_file = resource_dir / "logo.jpg"

def line_break(text: str, max_width: int) -> str:
    """
    将文字按照最大宽度进行换行
    """
    lines = []
    while len(text) > max_width:
        lines.append(text[:max_width])
        text = text[max_width:]
    print(lines)
    return '\n'.join(lines) + "\n" + text


def img_to_b64(pic: Image.Image) -> str:
    buf = BytesIO()
    pic.save(buf, format="PNG")
    base64_str = base64.b64encode(buf.getbuffer()).decode()
    return "base64://" + base64_str

async def make_jpg_new(text: str) -> Image.Image:
    logo = Image.open(logo_file)
    # emoji_font = ImageFont.truetype(emoji_font_file, size=30)
    zh_font = ImageFont.truetype(str(zh_font_file), size=30)
    name_font = ImageFont.truetype(str(zh_font_file), size=50)
    
    text1 = "欢迎"
    # text2 = text
    text2 = "「 {} 」".format(text)
    text3 = "加入网络安全协会"
    
    text1_w, text1_h = zh_font.getsize(text1)
    text2_w, text2_h = name_font.getsize(text2)
    text3_w, text3_h = zh_font.getsize(text3)
    
    all_h = text1_h + text2_h + text3_h
    
    new_img = Image.new('RGB', (logo.width, logo.height + all_h + 200), (0,0,0))
    # 居中 自动换行
    draw = Pilmoji(new_img)
    start_h = logo.height + 10
    draw.text(((logo.width - text1_w) / 2, start_h), text1, font=zh_font, fill=(255, 255, 255))
    
    max_width = int(logo.width / (zh_font.getsize('A')[0] * 2))
    
    text2_lines = line_break(text2, max_width).split('\n')
    print(text2_lines)
    start_h = start_h + text1_h 
    for i in range(len(text2_lines)):
        t_width, t_height = name_font.getsize(text2_lines[i])
        tmp_start_h = start_h + i * text2_h
        # tmp_start_w = (logo.width - t_width) // 2
        print(start_h)
        
        draw.text(((logo.width - t_width) // 2, tmp_start_h), text2_lines[i], font=name_font, fill="#c6e6e8")
    
    start_h = start_h + len(text2_lines) * text2_h + 30
    draw.text(((logo.width - text3_w) / 2, start_h ), text3, font=zh_font, fill=(255, 255, 255))
    # 将logo图片放在新图片上
    new_img.paste(logo, (0, 0))
    
    randomFilename = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 8)) + '.jpg'
    savePath = os.path.join(resource_dir, randomFilename)
    new_img.save(savePath)
    return savePath

@pic_gen.handle()
async def _pic_gen_handle(bot: Bot, event: Event, state: T_State):
    args = event.message.extract_plain_text().split(' ')
    if len(args) == 1:
        await bot.send(event, "请输入邀请函内容")
        return
    text = ' '.join(args[1:])
    title = '{}'.format(text)
    pic =await make_jpg_new(title)
    
    await bot.send(event, MessageSegment.image(img_to_b64(Image.open(pic))))
    os.remove(pic)
    return True

if __name__ == "__main__":
    make_jpg_new("text2_lines")