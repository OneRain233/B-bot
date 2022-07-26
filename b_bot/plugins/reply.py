from nonebot import on_command, on_startswith
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message


# reply = on_command("?", aliases={"回复", "自动回复"}, priority=5)
# reply = on_keyword(keywords=['?', '？'], priority=5)
reply = on_command("?", priority=5)

@reply.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    # res = await get_data()
    await reply.send("?")