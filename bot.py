import discord
import config
import voice_channel_status
import asyncio
import pytz
import flask_server
from datetime import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
from threading import Thread

client = discord.Client()
conf = config.Config
voice_channel_list = {}
line_bot_api = None
guild_id = 0


# ステータス確認
def get_h_m_s(td):
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


def get_time_str(duration):
    h, m, s = get_h_m_s(duration)
    if h > 0:
        return "%d時間" % h
    elif m > 0:
        return "%d分" % m
    elif s > 0:
        return "%d秒" % s


async def check_channel(guild_id):
    general_channel = client.get_channel(conf.general)
    while True:
        # await general_channel.send("test")
        await asyncio.sleep(conf.status_check_period)
        for id, voice_channel in voice_channel_list.items():
            channel = client.get_channel(id)

            # オフ0
            duration = datetime.now(pytz.timezone('Asia/Tokyo')) - voice_channel.last_changed_time
            if voice_channel.last_post_time:
                interval = (datetime.now(pytz.timezone('Asia/Tokyo')) - voice_channel.last_post_time).seconds
            else:
                interval = conf.post_interval
            if duration.seconds >= conf.timeout_time and interval >= conf.post_interval:
                if len(channel.members) == 1:
                    await general_channel.send("ほんでーかれこれまぁ%sくらい、えー待ったんですけども参加者は誰一人来ませんでした。" % get_time_str(duration))
                    voice_channel.post()

            # 複数人同ゲームプレイ時にオンラインユーザへinvite
            if voice_channel.last_invite_time:
                interval = (datetime.now(pytz.timezone('Asia/Tokyo')) - voice_channel.last_invite_time).seconds
            else:
                interval = conf.invite_interval

            if interval >= conf.invite_interval and len(channel.members) > 1:
                id = 0
                name = ""
                playing_same = True
                member_list = []
                for member in channel.members:
                    member_list.append(member.id)
                    if id == 0 and name == "":
                        if member.activity:
                            id = member.activity.application_id
                            name = member.activity.name
                        else:
                            playing_same = False
                            break
                    else:
                        if member.activity:
                            if member.activity.application_id != id:
                                playing_same = False
                                break
                        else:
                            playing_same = False
                            break
                if playing_same:
                    guild = client.get_guild(guild_id)
                    for user in guild.members:
                        if user.status == discord.Status.online and user.id not in member_list and user.id != conf.bot_id:
                            await general_channel.send("<@!%s> この辺でぇ、%s、やってるらしいっすよ。じゃけん参加しましょうね～" % (user.id, name))
                            # print(user.name)


async def delete_msg_loop():
    while True:
        await asyncio.sleep(conf.delete_period)
        await delete_msg()


# Botメッセージ削除
async def delete_msg():
    general_channel = client.get_channel(conf.general)
    async for message in general_channel.history(limit=200):
        if message.author.id == conf.bot_id:
            await message.delete()


@client.event
async def on_ready():
    general_channel = client.get_channel(conf.general)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    line_bot_api = LineBotApi(conf.line_access_token)
    print('Line bot initiated')
    print('------')

    async for guild in client.fetch_guilds(limit=1):
        guild_id = guild.id
    if guild_id == 0:
        exit(-1)
    guild = client.get_guild(guild_id)
    client.loop.create_task(check_channel(guild_id))
    for channel in guild.voice_channels:
        voice_channel_list[channel.id] = voice_channel_status.VoiceChannelStatus()
    await delete_msg()
    client.loop.create_task(delete_msg_loop())
    # await general_channel.send("で、でますよ")


@client.event
async def on_voice_state_update(member, before, after):
    # ステータス反映
    if after.channel:
        voice_channel_list[after.channel.id].status_change()
    if before.channel:
        voice_channel_list[before.channel.id].status_change()

    # メッセージ送信
    general_channel = client.get_channel(conf.general)
    if not before.channel and after.channel:
        channel_name = after.channel.name
        await general_channel.send("ウイイイイイイイッッッッス。どうも、%sでーす" % member.name)
        await general_channel.send("えーとですね、まぁ集合場所の、えー%sに行ってきたんですけども、ただいまの時刻は%s時を回りました" % (channel_name, datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%H")))
        messages = TextSendMessage(text=f"ウイイイイイイイッッッッス。どうも、{member.name}でーす")
        # line_bot_api.push_message(user_id, messages=messages)
    elif before.channel and not after.channel:
        channel_name = before.channel.name
        # await
        await general_channel.send("今日はここまでにしときます。それではみなさん、さよならー")
    # elif before.channel and after.channel and before.channel.name != after.channel.name:
    #     print("change")


job = Thread(target=flask_server.app_start)
job.start()
client.run(conf.token)
