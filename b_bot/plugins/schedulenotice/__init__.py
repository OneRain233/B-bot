from asyncio import events
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

get_schedule_monitor = on_command("schedule", permission=SUPERUSER, aliases={'查询课表'}, priority=1)
# # async def _temp_seting_handle(bot: Bot, event: Event, state: T_State):
#     args = event.message.extract_plain_text().split(' ')
#     status = args[1]

    
#     if status == "on":
#         with open(os.path.join(resource_dir, 'config.json'), 'r') as f:

#             j = json.load(f)
#             if event.group_id not in j['temp_group']:
#                 j["temp_group"].append(event.group_id)
#                 with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
#                     f.write(json.dumps(j))
#                 await bot.send(event, "温度开关已开启")
#             else:
#                 await bot.send(event, "温度开关已开启")
#     elif status == "off":
#         with open(os.path.join(resource_dir, 'config.json'), 'r') as f:
#             j = json.load(f)
#             if event.group_id in j['temp_group']:
#                 j["temp_group"].remove(event.group_id)
#                 with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
#                     f.write(json.dumps(j))
#                 await bot.send(event, "温度开关已关闭")
#             else:
#                 await bot.send(event, "温度开关已关闭")
#     elif status == 'set':
#         with open(os.path.join(resource_dir, 'config.json'), 'r') as f:
#             j = json.load(f)
#             msg = args[2:]
#             with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
#                 j["temp_msg"] = ' '.join(msg)
#                 f.write(json.dumps(j))
#             await bot.send(event, "温度消息已设置")
            
#     elif status == "test":
#         with open(os.path.join(resource_dir, 'config.json'), 'r') as f:
#             j = json.load(f)
#             await bot.send(event, j['temp_msg'])
@get_schedule_monitor.handle()
async def schedule_handle(bot: Bot, event: Event, state: T_State):
    plain_text = event.message.extract_plain_text().split(' ')
    arggs = plain_text.split(' ')
    if len(arggs) >= 1:
        week = arggs[1]
        if week.isdigit():
            week = int(week)
            qq_id = event.get_user_id()
            filepath = resource_dir + '/' + 'schedules/' + "{}.html".format(qq_id)
            await bot.send("2333")
            await get_schedule_monitor.finish(str(data.get_classes_by_week(week, filepath)))
        else:
            await get_schedule_monitor.finish("请输入正确的周数")
    else:
        await get_schedule_monitor.finish("请输入正确的周数")