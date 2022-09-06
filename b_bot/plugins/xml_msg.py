import json
from nonebot import on_command, on_startswith, on_notice,get_driver, get_bot
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
from mcstatus import JavaServer
from nonebot.rule import to_me
from nonebot.params import Arg, CommandArg, ArgPlainText, Command
from nonebot.adapters.onebot.v11 import Event, PokeNotifyEvent
import requests
from .pic_gen import img_to_b64
import random
from .txt2img import *
from pathlib import Path


xml_handle = on_command('xml', priority=1, block=False, rule=to_me())

@xml_handle.handle()
async def handle_first_receive(cmd = Command(), args = CommandArg()):
    await xml_handle.send(args)
    
    await xml_handle.send(MessageSegment.xml(str(args)))
    await xml_handle.finish()