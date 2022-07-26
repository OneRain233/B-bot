from nonebot import on_command, on_startswith, on_notice
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent
import base64



group_increase = on_notice(_group_increase, priority=10, block=True)


@group_increase.handle()
async def _group_increase(bot: Bot, event: GroupIncreaseNoticeEvent):
    return await group_increase.send(MessageSegment.at(event.get_user_id()) + "欢迎新朋友~")

