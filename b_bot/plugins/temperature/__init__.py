from asyncio import events
from json import load
import json
from pathlib import Path
from tokenize import group
from nonebot.permission import SUPERUSER

from ..txt2img import txt2img
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
from .report import report_temp
from nonebot import on_command, on_startswith, require, get_bot, get_driver

scheduler = require("nonebot_plugin_apscheduler").scheduler
temperatre_report = on_command("temp_report", aliases={"体温"}, permission=SUPERUSER)

@temperatre_report.handle()
async def _temperature_handler(bot: Bot, event: Event, state: T_State):
    await bot.send(event, "1")
    res = report_temp()
    await temperatre_report.finish(res)
    
    
# @scheduler.scheduled_job('cron', hour=7, minute=30)
# async def _report():

#     report_master = get_driver().config.dict().get('master', [])
#     if not report_master:
#         return
#     res = report_temp()
#     bot = get_bot()
#     for master in report_master:
#         await bot.send_private_msg(user_id=master, message=res)