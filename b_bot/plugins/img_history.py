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
import hashlib

img_history = on_command("img_history", aliases={"我要看黑历史","黑历史"})
upload_img = on_command("upload_img", aliases={"上传图片"})
img_md5_dict = {}

# resources/img/
resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'img')

def get_random_img():
    filelist = os.listdir(resource_dir)
    return random.choice(filelist)

def md5sum_all_img():
    global img_md5_dict
    md5_file = os.path.join(resource_dir, 'md5sum.json')
    all_img = os.listdir(resource_dir)
    for img in all_img:
        if img == 'md5sum.json':
            continue
        md5 = hashlib.md5(open(os.path.join(resource_dir, img), 'rb').read()).hexdigest()
        with open(md5_file, 'r') as f:
            md5_dict = json.load(f)
        md5_dict[img] = md5
        
        with open(md5_file, 'w') as f:
            f.write(json.dumps(md5_dict,indent=4))

    img_md5_dict = md5_dict


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
        # check md5sum
        md5sum = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
        if md5sum in img_md5_dict.values():
            # delete file
            os.remove(filepath)
            return 'md5'
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
            if filename and filename != 'md5':
                await bot.send(event, MessageSegment.image(img_to_b64(Image.open(os.path.join(resource_dir, filename)))))
                await bot.send(event, '图片上传成功')
                md5sum_all_img()
            elif filename == 'md5':
                await bot.send(event, '图片已存在')
        
    except Exception as e:
        await bot.send(event, "图片上传失败 {}".format(e))


md5sum_all_img()