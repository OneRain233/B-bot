from asyncio import events
from json import load
import json
from pathlib import Path
from tokenize import group
from nonebot import get_driver, on_command, get_bot, on_notice, on_request
from nonebot.permission import SUPERUSER

from ..txt2img import txt2img
from .plugins import data
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.adapters import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupBanNoticeEvent, MessageSegment, GroupRecallNoticeEvent
import datetime
import requests
from ..pic_gen import img_to_b64

resource_dir = str(Path() / 'data')
global_config = get_driver().config.dict()
start_week = global_config['start_week']
start_week = datetime.datetime.strptime(start_week, '%Y-%m-%d')
start_week = start_week.isocalendar()[1]
now_week = datetime.datetime.now().isocalendar()[1]

get_schedule_monitor = on_command("schedule",aliases={'查询课表'})
download_schdule_monitor = on_command("downloadSchedule", aliases={'下载课表'})
load_schedule_from_info_monitor = on_command("loadSchedule", aliases={'加载课表'})

@get_schedule_monitor.handle()
async def schedule_handle(bot: Bot, event: Event, state: T_State):
    plain_text = event.message.extract_plain_text()
    arggs = plain_text.split(' ')
    if len(arggs) >= 1:
        week = arggs[1]
        if week.isdigit():
            week = int(week)
            qq_id = event.get_user_id()
            filepath = resource_dir + '/' + 'schedules/' + "{}.html".format(qq_id)
            # check if file exists
            if not Path(filepath).exists():
                await get_schedule_monitor.send("您还没有课表，请先下载课表")
                await get_schedule_monitor.finish()
                
            await get_schedule_monitor.finish(str(data.get_classes_by_week(week, filepath)))
        else:
            await get_schedule_monitor.finish("请输入正确的周数")
    else:
        await get_schedule_monitor.finish("请输入正确的周数")
        
async def download_schedule(url, qq_id):
    filepath = resource_dir + '/' + 'schedules/' + "{}.html".format(qq_id)
    
    import requests
    req = requests.get(url)
    with open(filepath, 'wb') as f:
        f.write(req.content)
    
    return filepath

@download_schdule_monitor.handle()
async def download_schedule_handle(bot: Bot, event: Event, state: T_State):
    plain_text = event.message.extract_plain_text()
    arggs = plain_text.split(' ')
    if (len(arggs) > 1):
        url = arggs[1]
        qq_id = event.get_user_id()
        filepath = await download_schedule(url, qq_id)
        if filepath:
            await download_schdule_monitor.send("下载成功")
            await download_schdule_monitor.finish()
        else:
            await download_schdule_monitor.finish("下载失败")


@load_schedule_from_info_monitor.handle()
async def load_handler_1(bot: Bot, event: Event, state: T_State):
    # loadSchedule <课程代码> <年级> <班级>
    plain_text = event.message.extract_plain_text()
    arggs = plain_text.split(' ')
    code_res = resource_dir + "/" + "majorCode.json"
    j = json.loads(open(code_res).read())
    if(len(arggs) == 4):
        code = arggs[1]
        rank = arggs[2]
        classes = arggs[3].ljust(2, '0')
        p = code+rank+classes
        api = "http://jwc.swjtu.edu.cn/vatuu/CourseAction?setAction=printCourseTable&viewType=view&queryType=class&key={}&key_name=233&input_term_id=107&input_term_name=233".format(p)
        qq_id = event.get_user_id()
        filepath = await download_schedule(api, qq_id)
        if filepath:
            c_name = ""
            for i in j:
                if i['校内代码'] == code:
                    c_name = i['校内专业名称']
            await load_schedule_from_info_monitor.finish("加载{}{}-{}成功".format(c_name, rank, classes))
        else:
            await load_schedule_from_info_monitor.finish("加载失败")
    else:

        code = []
        for i in j:
            c = i['校内代码']
            name = i['校内专业名称']
            code.append(c+" "+name)
        reply_res = "\n".join(code)
        await load_schedule_from_info_monitor.send("loadSchedule <课程代码> <年级> <班级>\nExample: loadSchedule 0101 2020 01")
        img = txt2img(reply_res).save()
        msg = MessageSegment.image(img_to_b64(img))
        await load_schedule_from_info_monitor.finish(msg)