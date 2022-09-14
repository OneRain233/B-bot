from asyncio import events
from curses.ascii import isdigit
from json import load
import json
from pathlib import Path
from tokenize import group
from nonebot import get_driver, on_command, get_bot, on_notice, on_request,require
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
import os


notice_time = {
    1: "08:00",
    2: "09:50",
    3: "14:00",
    4: "15:50",
    5: "19:30"
}

resource_dir = str(Path() / 'data')
global_config = get_driver().config.dict()
start_week = global_config['start_week']
start_week = datetime.datetime.strptime(start_week, '%Y-%m-%d')
start_week = start_week.isocalendar()[1]
now_week = datetime.datetime.now().isocalendar()[1]

get_schedule_monitor = on_command("schedule",aliases={'查询课表'},priority=1, block=True, rule=to_me())
get_today_schedule_monitor =  on_command("today_schedule", aliases={'今日课表'},priority=1, block=True, rule=to_me())
download_schdule_monitor = on_command("downloadSchedule", aliases={'下载课表'},priority=1, block=True, rule=to_me())
load_schedule_from_info_monitor = on_command("loadSchedule", aliases={'加载课表'},priority=1, block=True, rule=to_me())
auto_notice_switch = on_command("schedule_notice", aliases={'课表提醒'}, priority=1, block=True, rule=to_me())
scheduler = require("nonebot_plugin_apscheduler").scheduler


@auto_notice_switch.handle()
async def _auto_notice_handle(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    welcome_config = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())
    argss = args.extract_plain_text().split()
    if len(argss ) == 0:
        await auto_notice_switch.finish("请输入开/关")
    ks = welcome_config.keys()
    if "notice_id" not in ks:
        welcome_config['notice_id'] = []
        filestream = open(os.path.join(resource_dir, 'config.json'), 'w')
        filestream.write(json.dumps(welcome_config))
        filestream.close()
    welcome_config = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())
    notice_id_list = welcome_config['notice_id']
    if argss[0] == "开":
        notice_id_list.append(event.get_user_id())
    elif argss[0] == '关':
        notice_id_list.remove(event.get_user_id())
        
    welcome_config['notice_id'] = notice_id_list
    with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
        f.write(json.dumps(welcome_config))
    await auto_notice_switch.finish("设置成功")
        
# add notice_time to scheduler
@scheduler.scheduled_job('interval', seconds=55)
async def _notice():
    week = now_week - start_week + 2
    weekday = datetime.datetime.now().weekday() + 1
    # now_time = datetime.datetime.now(tz=datetime.timezone.tzname('Asia/Shanghai')).strftime('%H:%M')
    asia_timezone = datetime.timezone(datetime.timedelta(hours=8))
    now_time = datetime.datetime.now(asia_timezone)
    
    for k,v in notice_time.items():
        if now_time == v:
            rank = k
            bot = get_bot()
            config_json = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())
            notice_ids = config_json['notice_id']
            for idd in notice_ids:
                # send private msg
                filepath = resource_dir + '/' + 'schedules/' + "{}.html".format(idd)
                today_class = data.get_class_by_week_and_day(week, weekday, filepath)
                if rank not in today_class.keys():
                    continue
                now_class = today_class[rank]
                class_name = now_class['class_name']
                classroom = now_class['classroom']
                await bot.call_api("send_private_msg", user_id=idd, message="现在是第{}节课:{}".format(rank, class_name+classroom))
                
                
        

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=7, minute=30, second=0)
async def daily_notice():
    welcome_config = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())
    ks = welcome_config.keys()
    if "schedule_notice_group" not in ks:
        welcome_config["schedule_notice_group"] = []
        filestream = open(os.path.join(resource_dir, 'config.json'), 'w')
        filestream.write(json.dumps(welcome_config))
        filestream.close()
        return
    week = now_week - start_week + 2
    weekday = datetime.datetime.now().weekday() + 1
    msg = ("今天是第{}周，周{}，发送“今日课表”查看今天的课表".format(week, weekday))
    for group_id in welcome_config["schedule_notice_group"]:
        bot = get_bot()
        await bot.call_api('send_group_msg', group_id=group_id, message=msg)


@get_today_schedule_monitor.handle()
async def _today_schedule(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    week = now_week - start_week + 2
    weekday = datetime.datetime.now().weekday() + 1
    
    qq_id = event.get_user_id()
    filepath = resource_dir + '/' + 'schedules/' + "{}.html".format(qq_id)
    if not Path(filepath).exists():
        await get_today_schedule_monitor.finish("请先下载课表")
        
    res = data.get_class_by_week_and_day(week, weekday, filepath)
    tmp_res = ""
    for rank in res.keys():
        t = "第{}讲({})：{} {}".format(rank, notice_time[rank], res[rank]['class_name'], res[rank]['classroom'])
        tmp_res += t + '\n'
    # await get_schedule_monitor.send(str(res))
    # await get_schedule_monitor.finish(str(tmp_res))
    await get_today_schedule_monitor.send("今天是第{}周，周{}".format(week, weekday))
    msg = "今天是第{}周，周{}".format(week, weekday) + "\n" + str(tmp_res)
    await get_today_schedule_monitor.finish(str(msg))


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
            res = data.get_classes_by_week(week, filepath)
            tmp_res = ""
            for week in res.keys():
                tmp_res += week + ":\n"
                for c in res[week]:
                    tmp_res += c + "\n"
                tmp_res += "\n"
            # await get_schedule_monitor.send(str(res))
            await get_schedule_monitor.finish(str(tmp_res))
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