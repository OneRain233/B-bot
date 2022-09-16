from nonebot import get_driver, on_command, get_bot, on_notice, on_request, on_message
from nonebot.permission import SUPERUSER
from .config import Config
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot.adapters import Message
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupBanNoticeEvent, MessageSegment, GroupRecallNoticeEvent, GroupRequestEvent
import json

global_config = get_driver().config.dict()

print(config)
superUsers = global_config['superusers']
print(superUsers)

# monitor  两个参数 user/msg
send_msg_monitor = on_command("send",permission=SUPERUSER, aliases={'发送'})
get_friends_list = on_command("friends", permission=SUPERUSER, aliases={'好友列表'})
get_group_list = on_command("groups",permission=SUPERUSER, aliases={'群列表'})
exit_group = on_command("exit", permission=SUPERUSER, aliases={'退群'})
revoke_msg = on_command("revoke", permission=SUPERUSER, aliases={'撤回'}, priority=1, block=True)
ban_user = on_command("禁言", aliases={'ban'}, priority=1, block=True)

def get_message_at(data: str) -> list:
    qq_list = []
    data = json.loads(data)
    try:
        for msg in data['original_message']:
            if msg['type'] == 'at':
                qq_list.append(int(msg['data']['qq']))
        return qq_list
    except Exception:
        return []

ban_session = {
    "00000000": {}
}
@ban_user.handle()
async def _ban_user(bot: Bot, event: Event):
    global ban_session
    # await ban_user.send(event.json())
    user_ids = []
    try:
        user_ids.append(event.reply.sender.user_id)
    except:
        user_ids = get_message_at(event.json())
    if not user_ids:
        await ban_user.finish("@一个人去禁言他")
    group_id = event.group_id
    try:
        group_session = ban_session[str(group_id)]
    except KeyError:
        ban_session[str(group_id)] = {}
        group_session = {}
    
    for i in user_ids:
        if int(i) == int(bot.self_id):
            await ban_user.finish("不要禁言弱弱bot")
        if str(i) in superUsers:
            await ban_user.finish("不要禁言弱弱superuser")
        if i in group_session.keys():
            data = group_session[i]
            if event.get_user_id() in data['flag']:
                await ban_user.finish("你已经投票过了")
                
            data['flag'].append(event.get_user_id())
            msg = "禁言id：{}\n禁言票数：{}/3".format(i, len(data['flag']))
            await ban_user.send(msg)
            if len(data['flag']) == 3:
                await bot.call_api('set_group_ban', group_id=group_id, user_id=i, duration=600)
                group_session.pop(i)
                ban_session[str(group_id)] = group_session
                
        else:
            new_ban_session = {
                "id": i,
                "group_id": group_id,
                "flag": [event.get_user_id()]
            }
            group_session[i] = new_ban_session
            ban_session[str(group_id)] = group_session
            msg = "禁言id：{}\n禁言票数：{}/3".format(i, len(new_ban_session['flag']))
            await ban_user.finish(msg)
        
    
    
@revoke_msg.handle()
async def _revoke_msg(bot: Bot, event: Event, state: T_State):
    # msg_id = event.get_message()
    if event.reply:
        msg_id = event.reply.message_id
        try:
            await bot.delete_msg(message_id=msg_id)
            await revoke_msg.finish()
        except Exception as e:
            await revoke_msg.finish()


@send_msg_monitor.handle()
async def handle_first_receive(bot:Bot,matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    arggs = plain_text.split(' ')
    if len(arggs) >= 3:
        msg = arggs[2:]
        msg = ' '.join(msg)
        type_ = arggs[0]
        user_id = arggs[1]

        userlist = await bot.call_api('get_friend_list')
        grouplist = await bot.call_api('get_group_list')
        userlist = [user['user_id'] for user in userlist]
        grouplist = [user['group_id'] for user in grouplist]
        if int(user_id) not in userlist and int(user_id) not in grouplist:
            await send_msg_monitor.send("userlist\n" + str(userlist))
            await send_msg_monitor.send("grouplist\n"+str(grouplist))
            await send_msg_monitor.finish("请输入正确的用户或群组qq")
        
        if "群聊" in str(type_):
            # await send_msg_monitor.send("111")
            await bot.call_api("send_group_msg", group_id=user_id, message=(msg))
        elif "私聊" in str(type_):
            # await send_msg_monitor.send("222")
            await bot.call_api('send_private_msg', user_id=user_id, message=(msg))
            
        await send_msg_monitor.finish(f"已经向{user_id}发送{msg}")


    await send_msg_monitor.send(plain_text)
    if plain_text:
        matcher.set_arg("msg", args) 
    
# 取得userid 和 msg
@send_msg_monitor.got("msg", prompt="请输入要发送的消息")
async def handle_msg(matcher: Matcher, msg: Message = Arg(), msg_txt: str = ArgPlainText("msg")):
    if str(msg) == 'cancle':
        await send_msg_monitor.finish("取消发送")
    matcher.set_arg("msg", msg)
    await send_msg_monitor.send(msg)
    
@send_msg_monitor.got("type", prompt="请输入要发送的类型 1:群聊 2:私聊")
async def handle_type(matcher: Matcher, _type: Message = Arg(), type_txt: str = ArgPlainText("type")):
    if str(type_txt) == 'cancle':
        await send_msg_monitor.finish("取消发送")
    if type_txt not in ['1', '2', '群聊', '私聊']:
        await send_msg_monitor.reject("请输入正确的类型")  
    
    matcher.set_arg("type", _type)
    
    await send_msg_monitor.send(_type)
    
@send_msg_monitor.got("user", prompt="请输入要发送的用户或群组qq")
async def handle_user(bot: Bot, matcher: Matcher, user: Message = Arg(), user_id: str = ArgPlainText("user")):
    if str(user) == 'cancle':
        await send_msg_monitor.finish("取消发送")
    await send_msg_monitor.send(user)
    userlist = await bot.call_api('get_friend_list')
    grouplist = await bot.call_api('get_group_list')
    userlist = [user['user_id'] for user in userlist]
    grouplist = [user['group_id'] for user in grouplist]
    if int(user_id) not in userlist and int(user_id) not in grouplist:
        await send_msg_monitor.send("userlist\n" + str(userlist))
        await send_msg_monitor.send("grouplist\n"+str(grouplist))
        await send_msg_monitor.reject("请输入正确的用户或群组qq")
    
    msg_txt = matcher.get_arg("msg")
    type_ = matcher.get_arg("type")
    # send private msg
    await send_msg_monitor.send(type_)
    if "群聊" in str(type_):
        # await send_msg_monitor.send("111")
        await bot.call_api("send_group_msg", group_id=user_id, message=msg_txt)
    elif "私聊" in str(type_):
        # await send_msg_monitor.send("222")
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
    
group_ban_= on_notice()
@group_ban_.handle()
async def group_ban_handle(bot: Bot, event: GroupBanNoticeEvent, state: T_State):
    ban_type = event.sub_type
    if ban_type == "ban":
        await group_ban_.send(f"是谁被禁言了我不说，嘿嘿嘿")
    elif ban_type == "lift_ban":
        pass

group_recall = on_notice()
@group_recall.handle()
async def group_recall_handle(bot: Bot, event: GroupRecallNoticeEvent, state: T_State):
    pass