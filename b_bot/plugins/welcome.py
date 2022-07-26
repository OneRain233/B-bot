from nonebot import on_notice
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent


async def _group_increase(bot: Bot, event: Event) -> bool:
    return isinstance(event, GroupIncreaseNoticeEvent)


group_increase = on_notice(_group_increase, priority=10, block=True)


@group_increase.handle()
async def _group_increase(bot: Bot, event: GroupIncreaseNoticeEvent):
    msg = "欢迎新朋友加入网络安全协会～\n宣传网页:http://swjtunsa.com/intro"
    return await group_increase.send(MessageSegment.at(event.get_user_id()) + msg)
