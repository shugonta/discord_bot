# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
import json
import config
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, JoinEvent, LeaveEvent, TextMessage, TextSendMessage
)

app = Flask(__name__)
conf = config.Config

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# @handler.add(MessageEvent, message=TextMessage)
# def message_text(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=event.message.text)
#     )

def load_json(filename):
    f = open(filename, 'r')
    data = json.loads(f)
    print(data)
    f.close()
    return data

def write_json(filename, data):
    f = open(filename, 'w')
    json.dump(data, f)
    print(json.dumps(data))
    f.close()

@handler.add(JoinEvent)
def join_event(event):
    if event.type == "join":
        group_id = 0
        type = event.source.type
        if type == "group":
            group_id = event.source.group_id
        if group_id != 0:
            f = open('grouplist.json', 'w')
            group_list = load_json(conf.json_file_name)
            if group_id not in group_list:
                group_list.append(group_id)
            write_json(conf.json_file_name, group_list)
    print(event)


@handler.add(LeaveEvent)
def leave_event(event):
    print(event)


def app_start():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# if __name__ == "__main__":
#     app_start()
