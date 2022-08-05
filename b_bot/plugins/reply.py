from nonebot import on_command, on_startswith, require, get_bot, get_driver
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
from nonebot.permission import SUPERUSER
import json
import os


work_dir = os.path.dirname(os.path.abspath(__file__))
resource_dir = os.path.join(work_dir, 'resources')
temp_setting = on_command("welcomeswitch", aliases={"tempeature_switch", "温度开关"}, permission=SUPERUSER)

scheduler = require("nonebot_plugin_apscheduler").scheduler

reply = on_command("?", priority=5)

@temp_setting.handle()
async def _temp_seting_handle(bot: Bot, event: Event, state: T_State):
    args = event.message.extract_plain_text().split(' ')
    status = args[1]

    
    if status == "on":
        with open(os.path.join(resource_dir, 'config.json'), 'r') as f:

            j = json.load(f)
            if event.group_id not in j['temp_group']:
                j["temp_group"].append(event.group_id)
                with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
                    f.write(json.dumps(j))
                await bot.send(event, "温度开关已开启")
            else:
                await bot.send(event, "温度开关已开启")
    elif status == "off":
        with open(os.path.join(resource_dir, 'config.json'), 'r') as f:
            j = json.load(f)
            if event.group_id in j['temp_group']:
                j["temp_group"].remove(event.group_id)
                with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
                    f.write(json.dumps(j))
                await bot.send(event, "温度开关已关闭")
            else:
                await bot.send(event, "温度开关已关闭")
    elif status == 'set':
        with open(os.path.join(resource_dir, 'config.json'), 'r') as f:
            j = json.load(f)
            msg = args[2:]
            with open(os.path.join(resource_dir, 'config.json'), 'w') as f:
                j["temp_msg"] = ' '.join(msg)
                f.write(json.dumps(j))
            await bot.send(event, "温度消息已设置")
            
    elif status == "test":
        with open(os.path.join(resource_dir, 'config.json'), 'r') as f:
            j = json.load(f)
            await bot.send(event, j['temp_msg'])

@reply.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    # res = await get_data()
    welcome_config = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())
    groups = welcome_config['reply_group']
    if event.group_id not in groups:
        return
    await reply.send("?")

# 每天早上8点提醒
@scheduler.scheduled_job('cron', hour="9-12/1", timezone='Asia/Shanghai')
async def scheduled_job():
    welcome_config = json.loads(open(os.path.join(resource_dir, 'config.json'), 'r', encoding='utf-8').read())
    ks = welcome_config.keys()
    if "temp_group" not in ks:
        welcome_config["temp_group"] = []
        filestream = open(os.path.join(resource_dir, 'config.json'), 'w')
        filestream.write(json.dumps(welcome_config))
        filestream.close()
        return
    for group_id in welcome_config["temp_group"]:
        bot = get_bot()
        await bot.call_api('send_group_msg', group_id=group_id, message=welcome_config['temp_msg'])
    
    
report_master = get_driver().config.dict().get('master', [])
@scheduler.scheduled_job('interval', seconds=60*30)
async def scheduled_report():
    if report_master == []:
        return

    bot = get_bot()
    for master in report_master:
        await bot.send_private_msg(user_id=master, message="我还活着!!")