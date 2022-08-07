from multiprocessing.context import SpawnContext
from random import random
from PIL import Image, ImageFont, ImageDraw
import sys
import time
from b_bot.plugins.pic_gen import img_to_b64
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
import random


class txt2img():
    def __init__(self, txt, img_path, font_size, font_path):
        self.txt = txt
        self.img_path = img_path
        self.font_size = font_size
        self.padding = 50
        self.spacing = 10
        self.margin = 10
        self.max_width = 1080
        self.font = ImageFont.truetype(font_path, self.font_size)

    def dertermin_txt_size(self, txt, spacing, right_paddind=0, left_padding=0):
        l = txt.split("\n")
        w = max([_ for _ in map(lambda x: self.font.getsize(x)[0], l)]) + right_paddind + left_padding
        h = sum([self.font.getsize(x)[1] for x in l]) + (len(l) - 1) * spacing
        return w, h

    def warp(self):
        res = ""
        t = self.txt.split("\n")
        max_char = int(self.max_width / self.font.getsize("a")[0])
        for i in t:
            while(len(i) > max_char):
                res += i[:max_char] + "\n"
                i = i[max_char:]
            res += i + "\n"
            # if len(i) > max_char:
            #     res += i[:max_char] + "\n"
            #     res += i[max_char:] + "\n"
            # else:
            #     res += i + "\n"
        return res


    def save(self):
        padding = self.padding
        spacing = self.spacing
        margin = self.margin
        self.txt = self.warp()
        w, h = self.dertermin_txt_size(self.txt, spacing, padding,padding)
        img = Image.new("RGB", (w,h + margin*2), (0, 0, 0))
        draw = ImageDraw.Draw(img)  
        draw.text((padding, margin), self.txt, (255, 255, 255), font=self.font, spacing=spacing)

        # img.save(self.img_path)
        # img.show()
        return img

txt2img_handler = on_command("txt2img", block=True)
resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
zh_font_file = os.path.join(resource_dir, 'font.ttf')
@txt2img_handler.handle()
async def _txt2img_handler(bot:Bot, event:Event):
    args = event.message.extract_plain_text().split(" ")
    # txt2img font_size txt
    if len(args) < 3:
        await bot.send(event, "txt2img font_size txt")
        return
    try:
        txt = " ".join(args[2:])
        font_size = int(args[1])
    except Exception as e:
        await bot.send(event, "txt2img font_size txt\n error: {}".format(e))
        return
    filename = str(random.randint(1,10000)) + ".png"
    filepath = os.path.join(resource_dir, filename)
    _txt2img = txt2img(txt, filepath, font_size, zh_font_file).save()
    
    msg = MessageSegment.image(img_to_b64(_txt2img))
    await bot.send(event, msg)
    try:
        os.remove(filepath)
    except Exception as e:
        pass
      
    


# if __name__ == "__main__":
#     txt2img("1223\n456\n789", "test.png",20).save()
