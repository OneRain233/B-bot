from distutils.command.upload import upload
import resource
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
from math import ceil
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg, ArgPlainText
from pathlib import Path


img_history = on_command("img_history", aliases={"我要看黑历史","黑历史"})
img_wall = on_command('img_wall', aliases={"黑历史墙"})
upload_img = on_command("upload_img", aliases={"上传图片"})
img_settings = on_command("img_settings", aliases={"黑历史设置"})
img_md5_dict = {}

# resources/img/
# resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'img')
resource_dir = str(Path() / "data" / "img_history")

@img_settings.handle()
async def _setting(bot: Bot, event:Event, matcher: Matcher, 
              msg: Message = CommandArg()):
    args = event.message.extract_plain_text().split(' ')
    status = args[1]
    
    if status == "reload":
        md5sum_all_img()
        await bot.send(event, "重载成功")

def get_random_img():
    filelist = os.listdir(resource_dir)
    return random.choice(filelist)

def generate_img_wall():
    # generate img wall in one img
    all_imgs = os.listdir(resource_dir)
    if 'md5sum.json' in all_imgs:
        all_imgs.remove('md5sum.json')
    
    img_num = len(all_imgs)
    if img_num == 0:
        return False
    img_sz = 600
    img_width = img_sz * 5
    img_height = img_sz * ceil(img_num / 5 )

    img = Image.new('RGB', (img_width, img_height), (255, 255, 255))
    
    x = 0
    y = 0
    for img_name in all_imgs:
        try:
            img_path = os.path.join(resource_dir, img_name)
            img_obj = Image.open(img_path)
        except Exception as e:
            pass
        # resize
        w,h = img_obj.size
        crop_size = min(w,h)
        # middle crop to 
        crop_pos = (
            (w - crop_size) / 2,
            (h - crop_size) / 2,
            (w + crop_size) / 2,
            (h + crop_size) / 2
        )
        try:
            img_obj = img_obj.crop(crop_pos)
            img_obj = img_obj.resize((img_sz, img_sz), Image.ANTIALIAS)
        except Exception as e:
            img_obj = img_obj.resize((img_sz, img_sz))
        img.paste(img_obj, (x, y))
        x += img_sz
        if x >= img_width:
            x = 0
            y += img_sz

    img = img.resize((img_width // 4, img_height // 4))
    # return img
    return img


def md5sum_all_img():
    global img_md5_dict
    md5_file = os.path.join(resource_dir, 'md5sum.json')
    all_img = os.listdir(resource_dir)
    md5_dict = {}
    for img in all_img:
        if img == 'md5sum.json':
            continue
        md5 = hashlib.md5(open(os.path.join(resource_dir, img), 'rb').read()).hexdigest()
        # with open(md5_file, 'r') as f:
        #     md5_dict = json.load(f)
        md5_dict[img] = md5
        
        # with open(md5_file, 'w') as f:
        #     f.write(json.dumps(md5_dict,indent=4))
    with open(md5_file, 'w') as f:
        f.write(json.dumps(md5_dict,indent=4))
        
    img_md5_dict = md5_dict

@img_wall.handle()
async def _img_wall(bot: Bot, event: Event):
    await bot.send(event, '删了，爬')
    return
    img = generate_img_wall()
    if img:
        b64 = img_to_b64(img)
        await bot.send(event, MessageSegment.image(b64))
    else:
        await bot.send(event, '没有图片')


@img_history.handle()
async def img_handle(bot: Bot, event: Event, state:T_State):
    await bot.send(event,"删了，爬")
    return
    img = get_random_img()
    img_file = os.path.join(resource_dir, img)
    img = Image.open(img_file)
    await bot.send(event, MessageSegment.image(img_to_b64(img)))

async def download_img(url):
    try:
        md5sum_all_img()
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