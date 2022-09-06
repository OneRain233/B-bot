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


cc = on_command("cc")
global_config = get_driver().config.dict()
superUsers = global_config['superusers']

def get_data(s):
    try:
        magic_api = global_config['cyberchef_api'] + "/magic"
        bake_api = global_config['cyberchef_api'] + "/bake"
    except Exception as e:
        return False
    data = {
        "input": s
    }
    res = requests.post(magic_api, json=data)
    j = res.json()
    print(j['value'])
    values = j['value']
    ret = []
    for value in values:
        r = ["{} {}".format(i['op'], i['args']) for i in value['recipe']]
        if len(value['data'] ) < 100:
            ret.append(
                "Value: \n" + str(value['data']) + "\nRecipe: \n" + " -> ".join(r)
            )
            continue
        new_data = {
            "input": s,
            "recipe": value['recipe']
        }
        print(json.dumps(new_data))
        new_res = requests.post(bake_api, json=new_data)
        new_j = new_res.json()
        new_value = new_j['value']
        new_type = new_j['type']
        
        if new_type == "byteArray":
            # to hex
            ss = ""
            for i in new_value:
                ss += chr(i)
            new_value = ss
                
        
        ret.append(
            "Value: \n" + str(new_value) + "\nRecipe: \n" + " -> ".join(r) + "\nType:" + str(new_type)
        )
    
    # delete the last element of ret
    ret = ret[:-1]
    return ret

@cc.handle()
async def cc_handler(cmd = Command(), args = CommandArg()):
    # await cc.send(cmd)
    # await cc.send(str(args))
    arggs = str(args).split(" ")

    user_input = ' '.join(arggs[0:])
    
    data = get_data(user_input)
    if not data:
        await cc.send("cyberchef_api not set")
        
    msg = "\n\n".join(data)
    try:
        await cc.send(msg)
    except Exception as e:
        img = txt2img(msg).save()
        msg = MessageSegment.image(img_to_b64(img))
        await cc.send(msg)
    