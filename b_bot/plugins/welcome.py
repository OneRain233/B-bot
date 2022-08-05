from nonebot import on_notice, on_command, permission, CommandGroup
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent
import os
import json
from .pic_gen import img_to_b64, make_jpg_new
from PIL import Image, ImageDraw, ImageFont


async def _group_increase(bot: Bot, event: Event) -> bool:
    return isinstance(event, GroupIncreaseNoticeEvent)


async def _group_decrease(bot: Bot, event: Event) -> bool:
    return isinstance(event, GroupDecreaseNoticeEvent)

group_increase = on_notice(_group_increase, priority=10, block=True)
group_decrease = on_notice(_group_decrease, priority=10, block=True)
setting = on_command("welcomeswitch", aliases={"欢迎开关"})


work_dir = os.path.dirname(os.path.abspath(__file__))
resource_dir = os.path.join(work_dir, 'resources')

try:
    filestream = open(os.path.join(resource_dir, 'config.json'), 'r')
except FileNotFoundError:
# create config file
    filestream = open(os.path.join(resource_dir, 'config.json'), 'w')
    welcome_msg = "welcome to this group"
    j = {
        "welcome_msg": welcome_msg,
        "group_id": []
    }
    filestream.write(json.dumps(j))
    filestream.close()

@setting.handle()
async def _seting_handle(bot: Bot, event: Event, state: T_State):
    args = event.message.extract_plain_text().split(' ')
    status = args[1]
    if status == "on":
        with open(os.path.join(resource_dir, 'config.json'), 'r') as f:

            j = json.load(f)
            if event.group_id not in j['group_id']:
                j["group_id"].append(event.group_id)
                with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
                    f.write(json.dumps(j))
                await bot.send(event, "欢迎开关已开启")
            else:
                await bot.send(event, "欢迎开关已开启")
    elif status == "off":
        with open(os.path.join(resource_dir, 'config.json'), 'r') as f:
            j = json.load(f)
            if event.group_id in j['group_id']:
                j["group_id"].remove(event.group_id)
                with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
                    f.write(json.dumps(j))
                await bot.send(event, "欢迎开关已关闭")
            else:
                await bot.send(event, "欢迎开关已关闭")

    elif status == "test":
        welcome_config = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())
        print(event)
        group_id = event.group_id
        if group_id not in welcome_config['group_id']:
            return
        msg = welcome_config['welcome_msg']
        # msg = "欢迎新朋友加入网络安全协会～\n宣传网页:http://swjtunsa.com/intro\n问卷：https://docs.qq.com/form/page/DQU95T2h1dHR4VVFO"
        await bot.send(event, msg)

        try:
            nickname = await bot.get_group_member_info(group_id=group_id, user_id=event.user_id)
            nickname = nickname['nickname']
            pic =await make_jpg_new(nickname)
            await bot.send(event, MessageSegment.image(img_to_b64(Image.open(pic))))
            os.remove(pic)
        except Exception as e:
            print(e)
            # await bot.send(event, str(e))

@group_increase.handle()
async def _group_increase(bot: Bot, event: GroupIncreaseNoticeEvent):

    welcome_config = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())

    group_id = event.group_id
    if group_id not in welcome_config['group_id']:
        return

    msg = welcome_config['welcome_msg']
    # msg = "欢迎新朋友加入网络安全协会～\n宣传网页:http://swjtunsa.com/intro\n问卷：https://docs.qq.com/form/page/DQU95T2h1dHR4VVFO"
    await bot.send(event, msg)

    try:
        nickname = await bot.get_group_member_info(group_id=group_id, user_id=event.user_id)
        nickname = nickname['nickname']
        pic =await make_jpg_new(nickname)
        await bot.send(event, MessageSegment.image(img_to_b64(Image.open(pic))))
        os.remove(pic)
    except Exception as e:
        print(e)
        # await bot.send(event, str(e))

@group_decrease.handle()
async def _group_decrease(bot: Bot, event: GroupDecreaseNoticeEvent):
    welcome_config = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())

    group_id = event.group_id
    if group_id not in welcome_config['group_id']:
        return

    msg = "你们把人吓跑了！！！！！"
    return await group_decrease.send(msg) 