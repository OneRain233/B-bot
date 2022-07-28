from nonebot import on_command, on_startswith, require, get_bot, get_driver
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
import json
import os


work_dir = os.path.dirname(os.path.abspath(__file__))
resource_dir = os.path.join(work_dir, 'resources')

scheduler = require("nonebot_plugin_apscheduler").scheduler


# reply = on_command("?", aliases={"回复", "自动回复"}, priority=5)
# reply = on_keyword(keywords=['?', '？'], priority=5)
reply = on_command("?", priority=5)

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
        await bot.call_api('send_group_msg', group_id=group_id, message="几点了？体温填了吗？快去填体温～～～～")
    
    
report_master = get_driver().config.dict().get('master', [])
# 每2s上报
@scheduler.scheduled_job('interval', seconds=60*30)
async def scheduled_report():
    if report_master == []:
        return

    bot = get_bot()
    for master in report_master:
        await bot.send_private_msg(user_id=master, message="我还活着!!")