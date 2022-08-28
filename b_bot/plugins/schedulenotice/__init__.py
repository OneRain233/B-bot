from pathlib import Path
from tokenize import group
from nonebot import get_driver, on_command, get_bot, on_notice, on_request
from nonebot.permission import SUPERUSER
from .plugins import data
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.adapters import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupBanNoticeEvent, MessageSegment, GroupRecallNoticeEvent
import datetime

resource_dir = str(Path() / 'data')
global_config = get_driver().config.dict()
start_week = global_config['start_week']
start_week = datetime.datetime.strptime(start_week, '%Y-%m-%d')
start_week = start_week.isocalendar()[1]
now_week = datetime.datetime.now().isocalendar()[1]

get_schedule_monitor = on_command("schedule", permission=SUPERUSER, aliases={'查询课表'})

@get_schedule_monitor.handle()
async def _handle(bot:Bot,matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    arggs = plain_text.split(' ')
    if len(arggs) >= 1:
        week = arggs[0]
        if week.isdigit():
            week = int(week)
            filepath = resource_dir + '/' + "test.html"
            await get_schedule_monitor.finish(str(data.get_classes_by_week(week, filepath)))
        else:
            await get_schedule_monitor.finish("请输入正确的周数")
    else:
        await get_schedule_monitor.finish("请输入正确的周数")