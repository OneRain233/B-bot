from nonebot import on_command, on_startswith, on_notice
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import *
import base64


# reply = on_command("?", aliases={"回复", "自动回复"}, priority=5)
# reply = on_keyword(keywords=['?', '？'], priority=5)
org_welcome = on_command("welcome", priority=5)
"""
07-25 11:20:24 [SUCCESS] nonebot | ONEBOT V11 2492994043 | [notice.group_recall]: {'time': 1658747995, 'self_id': 2492994043, 'post_type': 'notice', 'notice_type': 'group_recall', 'user_id': 1193498985, 'group_id': 912740210, 'operator_id': 1193498985, 'message_id': 2087683988}"""



@org_welcome.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    # res = await get_data()
    # send img
    img = open('b_bot/plugins/resources/welcome.jpg', 'rb')
    # base64_data = "data:image/jpeg;base64," + base64.b64encode(img.read()).decode()

    await org_welcome.send(MessageSegment.image("https://gchat.qpic.cn/gchatpic_new/2492994043/984900265-2602726215-62A6608E2AF1A3E2E82C7E766C61A66E/0?term=255"))
