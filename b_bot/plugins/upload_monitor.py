from nonebot import on_notice, on_command, permission, CommandGroup
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent, GroupUploadNoticeEvent
import os
import json
from .pic_gen import img_to_b64, make_jpg_new
from PIL import Image, ImageDraw, ImageFont


async def _upload_monitor(bot: Bot, event: Event) -> bool:
    return isinstance(event, GroupUploadNoticeEvent)


upload_monitor = on_notice(priority=10, block=True)


# [notice.group_upload]: 
# {'time': 1658999484, 'self_id': 2492994043, 'post_type': 'notice', 'notice_type': 'group_upload', 'user_id': 76054204, 'group_id': 984900265, 
# 'file': {'id': '/1a85f69d-8647-44f9-9b0b-e4cec863c468', 
#       'name': 'generate.py', 'size': 917, 'busid': 102, 
#       'url': 'http://42.81.232.83/ftn_handler/5bea04a0c09ebb433d05201ae88d32bf8cf2b7c3b252e6a07baa8778f4e7947d410d629f9e6a350caf46298f0d924a35e50f7b6c922205b3cf930bd1209796b3/?fname=2f31613835663639642d383634372d343466392d396230622d653463656338363363343638'
#      }
# }
@upload_monitor.handle()
async def _monitor(bot: Bot, event: GroupUploadNoticeEvent, state: T_State):
    filename = event.file.name
    user = event.user_id
    url = event.file.url
    
    msg = f"{user}上传了文件{filename}\n直链:{url}"
    await bot.send(event, msg)
    