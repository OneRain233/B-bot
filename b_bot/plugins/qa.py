import resource
from nonebot import on_command, on_startswith, require, get_bot, get_driver, on_message, on_regex
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.params import Arg, CommandArg, ArgPlainText
import json
import os
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PokeNotifyEvent,
)
import re
from pathlib import Path
from .pic_gen import img_to_b64
import random
from .txt2img import *
from pathlib import Path

work_dir = os.path.dirname(os.path.abspath(__file__))
# resource_dir = os.path.join(work_dir, 'resources')
resource_dir = str(Path() / "data")
db_file = os.path.join(resource_dir, 'qa.json')
welcome_db_file = os.path.join(resource_dir, 'welcome.json')
config_file = os.path.join(resource_dir, 'config.json')
questions = {}

ask = on_regex(r"想问|请问", priority=5, block=False) # 猜你想问
qa_handler = on_command("qa", aliases={"问答"}, permission=SUPERUSER, priority=1)
qa_setting = on_command("qa_setting", aliases={"问答"}, permission=SUPERUSER, priority=1)
qa = on_message(block=False)
human_help = on_command("human_help", aliases={"人工", "转人工"})

@human_help.handle()
async def _human_help_handle(bot: Bot, event: Event, state: T_State):
    human_help_list = await bot.call_api("get_group_member_list", group_id=event.group_id)
    manager_list = []
    for i in human_help_list:
        if i["role"] == "owner" or i["role"] == "admin":
            manager_list.append(i["user_id"])
    await human_help.finish("有人需要帮助，" + MessageSegment.at(random.choice(manager_list)) + "为你服务")
    
@ask.handle()
async def _ask_handle(bot: Bot, event: Event, state: T_State):
    msg = []
    msg.append("=====猜你想问=====")
    with open(welcome_db_file, 'r', encoding='utf-8') as f:
        j = json.load(f)
    for k in j.keys():
        msg.append(k)
    msg = "\n".join(msg)
    img = txt2img(msg).save()
    msg = MessageSegment.image(img_to_b64(img))
    human_help_list = await bot.call_api("get_group_member_list", group_id=event.group_id)
    manager_list = []
    for i in human_help_list:
        if i["role"] == "owner" or i["role"] == "admin":
            manager_list.append(i["user_id"])
        
    await ask.send("猜你想问：\n" + msg + "\n回复问题即可查看答案" + "\n人工 可以转接" )
    await ask.finish()

        
        

@qa_setting.handle()
async def _setting(bot: Bot, event:Event, matcher: Matcher, 
              msg: Message = CommandArg()):
    args = event.message.extract_plain_text().split(' ')
    status = args[1]
    
    if status == "reload":
        get_all_questions()
        await bot.send(event, "重载成功")
    elif status == "on":
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if event.group_id not in config['qa']:
                
                config['qa'].append(event.group_id)
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
                    await bot.send(event, "添加成功")
                    return True
            else:
                await bot.send(event, "已经开启过了")
                
    elif status == "off":
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if event.group_id in config['qa']:
                config['qa'].remove(event.group_id)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
                    await bot.send(event, "关闭成功")
                    return True
            else:
                await bot.send(event, "没有开启过")
        

async def get_answer(question):
    # match the question 
    # _quesions = questions.keys()
    # for q in _quesions:
    #     if q in question:
    #         return questions[q]
    # return None
    return questions.get(question, None)

async def set_answer(question, answer):
    # append
    with open(db_file, 'r', encoding='utf-8') as f:
        db = json.load(f)
        db[question] = answer
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
            return True
    return False
            
def get_all_questions():
    global questions
    with open(db_file, 'r', encoding='utf-8') as f:
        db = json.load(f)
        questions = db
    #append welcome
    with open(welcome_db_file, 'r', encoding='utf-8') as f:
        db = json.load(f)
        for k in db.keys():
            questions[k] = db[k]
        
    return questions

def parse_args(s):
    q = ""
    a = ""
    # "question" "answer"
    pattern = re.compile(r'"(.*?)" "(.*?)"')
    matches = pattern.findall(s)

    if len(matches) == 0:
        return None
    else:
        q = matches[0][0]
        a = matches[0][1]
        return (q, a)
    
    
    

@qa_handler.handle()
async def _handlers(bot: Bot, event:Event, matcher: Matcher, 
              msg: Message = CommandArg()):
    message = msg.extract_plain_text().strip().split()
    if not message or len(message) < 2:
        await bot.send(event, '请输入问题 和 答案')
        return
    try:
        question, answer = parse_args(msg.extract_plain_text())
    except Exception as e:
        question = message[0]
        answer = " ".join(message[1:])
    if "\\n" in answer:
        # answer = answer.replace("\\n", "\n")
        tmp = answer.split("\\n")
        answer = ""
        for i in tmp:
            answer += i.strip() + "\n"
    if "\\n" in question:
        tmp = question.split("\\n")
        question = ""
        for i in tmp:
            question += i.strip() + "\n"    
    if not question or not answer:
        await bot.send(event, '请输入问题 和 答案')
        return 
    # question = message[0]
    # answer = " ".join(message[1:])
    res = await set_answer(question, answer)
    if res:
        await bot.send(event, "问题：{}\n答案：{}".format(question, answer))
        get_all_questions()
    else:
        await bot.send(event, "Error")
    
@qa.handle()
async def _qa(bot:Bot,event: MessageEvent):
    config = open(config_file, 'r', encoding='utf-8')
    j = json.load(config)
    try:
        if event.group_id not in j['qa']:
            return
    except:
        return
    message = event.message.extract_plain_text().strip().split()
    if not message:
        return
    question = " ".join(message)
    try:
        ans = await get_answer(question)
        await bot.send(event, ans)
    except Exception as e:
        print(e)
        # await bot.send(event, "没有找到答案") 
        
get_all_questions()