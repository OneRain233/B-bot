from nonebot import on_command, on_startswith, on_notice, get_bot, on_message, get_driver
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import *
import base64
import random


global_config = get_driver().config.dict()
superUsers = global_config['superusers']

# private message listener
listener = on_message(priority=1, block=False, rule=to_me())

@listener.handle()
async def handle_first_receive(bot: Bot, event: Event):
    message = event.get_message()
    res = "{}：\n{}".format(event.get_user_id(), message)
    for su in superUsers:
        await bot.send_private_msg(user_id=su, message=res)
