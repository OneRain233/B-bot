from nonebot import on_command, on_startswith, on_notice
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
from mcstatus import JavaServer
from nonebot.rule import to_me
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Event, PokeNotifyEvent
# 戳一戳
mc = on_notice(rule=to_me())

@mc.handle()
async def mc_status(bot: Bot, event: PokeNotifyEvent, state: T_State):
    server = JavaServer(host="1.15.105.102", port=10001)
    status = server.status().latency
    msg = """
    Ping: {}
    Online: {}
    """.format(status, server.status().players.online)
    # print(msg)
    await bot.send(event, msg)