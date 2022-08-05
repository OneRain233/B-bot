from nonebot import on_command, on_startswith, require, get_bot, get_driver, on_message
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


work_dir = os.path.dirname(os.path.abspath(__file__))
resource_dir = os.path.join(work_dir, 'resources')
db_file = os.path.join(resource_dir, 'qa.json')
config_file = os.path.join(resource_dir, 'config.json')
questions = {}


qa_handler = on_command("qa", aliases={"问答"}, permission=SUPERUSER, priority=1)
qa = on_message(block=False)

async def get_answer(question):
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
        return questions
    
@qa_handler.handle()
async def _handlers(bot: Bot, event:Event, matcher: Matcher, 
              msg: Message = CommandArg()):
    message = msg.extract_plain_text().strip().split()
    if not message or len(message) < 2:
        await bot.send(event, '请输入问题 和 答案')
        return
    question = message[0]
    answer = message[1:]
    res = await set_answer(question, answer)
    if res:
        await bot.send(event, "问题：{}\n答案：{}".format(question, answer))
        get_all_questions()
    else:
        await bot.send(event, "没有找到相关问题")
    
@qa.handle()
async def _qa(bot:Bot,event: MessageEvent):
    message = event.message.extract_plain_text().strip().split()
    if not message:
        return
    question = message[0]
    try:
        ans = await get_answer(question)
        await bot.send(event, ans)
    except Exception as e:
        print(e)
        # await bot.send(event, "没有找到答案")
        
get_all_questions()