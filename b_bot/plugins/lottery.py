from nonebot import on_command, on_startswith, on_notice, get_bot
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import *
import base64
import random


lottery = on_command("lottery")

@lottery.handle()
async def lottery_receive(bot: Bot, event: Event, state: T_State):
    members = await bot.get_group_member_list()
    members = [member.user_id for member in members]
    winner = random.choice(members)
    lottery_msg = "恭喜{}获奖～".format(await bot.get_group_member_info(event.group_id, winner))
    await lottery.send(lottery_msg)
    