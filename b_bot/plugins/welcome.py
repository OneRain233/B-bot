from nonebot import on_command, on_startswith, on_notice
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import *
import base64



welcome = on_notice()


# 入群提醒
@welcome.handle()
async def welcome_group(bot: Bot, event: GroupIncreaseNoticeEvent, state: T_State):
    welcome.send(event, "欢迎新人~~~~~~~看下群公告哦(｡･ω･｡)")

