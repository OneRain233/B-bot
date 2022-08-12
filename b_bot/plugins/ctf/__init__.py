from os import stat
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import os
from nonebot.adapters.onebot.v11 import MessageSegment
from ..txt2img import txt2img
from ..img_history import img_to_b64
from pathlib import Path

# resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')
resource_dir = Path() / "data" / "resources"
font_dir = Path() / "data" / "fonts"
# zh_font_file = os.path.join(resource_dir, 'font.ttf')
zh_font_file = font_dir / "font.ttf"

ctflist = on_command('ctflist', priority=1, aliases={'我要打ctf'})
ctfinfo = on_command('ctfinfo', priority=1)
@ctflist.handle()
async def _(bot: Bot, event: Event, state: T_State):
    from .ctf_api import ctf_list
    res = ctf_list()
    # print(res)
    img = txt2img(res).save()
    msg = MessageSegment.image(img_to_b64(img))
    await ctflist.send( msg)

@ctfinfo.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = event.message.extract_plain_text().split(' ')
    if len(args) == 2:
        state['num'] = args[1]
    
async def get_data(num):
    import datetime
    from .ctf_api import ctf_info
    raw = (ctf_info(num))
    ida = raw['id']
    details = "\n".join([i.strip() for i in raw['details'].split('\n')])
    start_time = datetime.datetime.fromtimestamp(raw['start_time'])
    end_time = datetime.datetime.fromtimestamp(raw['end_time'])
    form = raw['form'].strip()
    official_url = raw['official_url'].strip()
    title = raw['title'].strip()
    temp = """
    id: {}
    Title: {}
    URL: {}
    Start Time: {}
    End Time: {}
    Details:
    =========================================
    {}
    =========================================
    """.format(ida, title, official_url, start_time, end_time, details)
    # temp = "id: " + str(ida) + "\n" + "Title: " + str(title) + "\n" + "Start: " + str(
    #     start_time) + "\n" + "End: " + str(end_time) + "\n" + "Details: \n" + str(details) + "\n" + "url: " + str(
    #     official_url)
    return temp

@ctfinfo.got('num', prompt='请输入序号')
async def __(bot: Bot, event: Event, state: T_State):

    num = int(state['num'])
    temp = await get_data(num)

    img = txt2img(temp).save()
    msg = MessageSegment.image(img_to_b64(img))
    await ctfinfo.send(temp)
    await ctfinfo.finish(msg)
