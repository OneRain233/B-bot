from nonebot import on_command, on_startswith, on_notice
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import *
import base64


# reply = on_command("?", aliases={"回复", "自动回复"}, priority=5)
# reply = on_keyword(keywords=['?', '？'], priority=5)
org_welcome = on_command("welcome", priority=5)
# 问卷
quiz = on_command("quiz", aliases={"问卷", "问卷调查"}, priority=5)

@org_welcome.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    # res = await get_data()
    # send img
    img = open('b_bot/plugins/resources/welcome.jpg', 'rb')
    # base64_data = "data:image/jpeg;base64," + base64.b64encode(img.read()).decode()

    await org_welcome.send(MessageSegment.image("http://193.203.13.126:8080/directlink/od/QQ_Image_1658889267416.jpg"))

@quiz.handle()
async def handle_quiz_receive(bot: Bot, event: Event, state: T_State):
    msg = "【腾讯文档】2022网络安全协会招新 https://docs.qq.com/form/page/DQU95T2h1dHR4VVFO"
    await quiz.send(msg)