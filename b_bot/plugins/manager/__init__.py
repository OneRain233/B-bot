from nonebot import get_driver, on_command, get_bot
from nonebot.permission import SUPERUSER
from .config import Config
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.adapters import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.rule import to_me

global_config = get_driver().config.dict()
# report_master = get_driver().config.dict().get('master', [])

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

print(config)
superUsers = global_config['superusers']
print(superUsers)

# monitor  两个参数 user/msg
send_msg_monitor = on_command("send",permission=SUPERUSER, aliases={'发送'})
get_friends_list = on_command("friends", permission=SUPERUSER, aliases={'好友列表'})
get_group_list = on_command("groups",permission=SUPERUSER, aliases={'群列表'})
exit_group = on_command("exit", permission=SUPERUSER, aliases={'退群'})

@send_msg_monitor.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if plain_text:
        matcher.set_arg("msg", args)  # 如果用户发送了参数则直接赋值
    
# 取得userid 和 msg
@send_msg_monitor.got("msg", prompt="请输入要发送的消息")
async def handle_msg(matcher: Matcher, msg: Message = Arg(), msg_txt: str = ArgPlainText("msg")):
    matcher.set_arg("msg", msg)
    await send_msg_monitor.send(msg)
    
@send_msg_monitor.got("type", prompt="请输入要发送的类型 1:群聊 2:私聊")
async def handle_type(matcher: Matcher, _type: Message = Arg(), type_txt: str = ArgPlainText("type")):
    if type_txt not in ['1', '2']:
        await send_msg_monitor.reject("请输入正确的类型")  
    
    matcher.set_arg("type", _type)
    
    await send_msg_monitor.send(_type)
    
@send_msg_monitor.got("user", prompt="请输入要发送的用户或群组qq")
async def handle_user(bot: Bot, matcher: Matcher, user: Message = Arg(), user_id: str = ArgPlainText("user")):
    await send_msg_monitor.send(user)
    userlist = await bot.call_api('get_friend_list')
    grouplist = await bot.call_api('get_group_list')
    userlist = [user['user_id'] for user in userlist]
    if int(user_id) not in userlist and int(user_id) not in grouplist:
        await send_msg_monitor.send(str(userlist))
        await send_msg_monitor.reject("请输入正确的用户或群组qq")
    
    msg_txt = matcher.get_arg("msg")
    type_ = matcher.get_arg("type")
    # send private msg
    if type_ == "1":
        await bot.call_api("send_group_msg", group_id=user_id, message=msg_txt)
    else:
        await bot.call_api('send_private_msg', user_id=user_id, message=msg_txt)
        
    await send_msg_monitor.finish(f"已经向{user_id}发送{msg_txt}")

@get_group_list.handle()
async def groups_handle(bot: Bot, event: Event, state: T_State):
    group_list = await bot.call_api('get_group_list')
    # await bot.send(event, f"{group_list}")
    group_list = [str((group['group_id'], group['group_name'])) for group in group_list]
    msg = "\n".join(group_list)
    await bot.send(event, f"{msg}")
    
@get_friends_list.handle()
async def friends_handle(bot: Bot, event: Event, state: T_State):
    friend_list = await bot.call_api('get_friend_list')
    friend_list = [str((friend['user_id'], friend['nickname'])) for friend in friend_list]
    msg = "\n".join(friend_list)
    await bot.send(event, f"{msg}")
    
@exit_group.handle()
async def exit_group_handle(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    
    if args:
        matcher.set_arg("group_id", args)
        
@exit_group.got("group_id", prompt="请输入要退出的群组qq")
async def exit_group_got(bot: Bot, matcher: Matcher, group_id: str = ArgPlainText("group_id")):
    await exit_group.send(f"你将要退出{group_id}")
    await bot.call_api('set_group_leave', group_id=group_id)
    await exit_group.finish(f"已经退出{group_id}")
    
@join_group.handle()
async def join_group_handle(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    if args:
        matcher.set_arg("group_id", args)
