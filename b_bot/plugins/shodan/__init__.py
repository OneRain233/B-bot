from nonebot import get_driver, get_bot

from .config import *
from nonebot_plugin_apscheduler import scheduler
from .shodan_monitor import _find   

@scheduler.scheduled_job('interval', seconds=interval)
async def _():
    print("[*] Start to scan Shodan")
    res = await _find()
    if res:
        await get_bot().call_api('send_group_msg', group_id="984900265", message=res)