# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from argparse import ArgumentParser
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, LocationMessage, LocationSendMessage, SourceGroup, SourceRoom
from modules import opt_route
import names
from datetime import datetime

app = Flask(__name__)
token = os.environ['TOKEN']
secret_key = os.environ['SECRET']
line_bot_api = LineBotApi(token)
handler = WebhookHandler(secret_key)

swarmsize = int(os.environ['SWARMSIZE'])
maxiter = int(os.environ['MAXITER'])

# create user stats dictionary
user_dict = {}

class UserStatus():
    def __init__(self):
        self.state = "waiting"
        self.coord = []
        self.isexplained = False

    def clear(self):
        self.state = "waiting"
        self.coord = []


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    # try:
    handler.handle(body, signature)
    # except InvalidSignatureError:
    #     abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if isinstance(event.source, SourceGroup):
        id = event.source.group_id
    elif isinstance(event.source, SourceRoom):
        id = event.source.room_id
    else:
        id = event.source.user_id
    if not id in user_dict:
        user_dict[id] = UserStatus()

    text = event.message.text
    if text == "手伝って" and user_dict[id].state == "waiting":
        user_dict[id].state = "collecting_coordination"
        line_bot_api.reply_message(event.reply_token,
                                   [TextSendMessage(text="かしこまりました"), TextSendMessage(text="位置情報を教えてください")])
    elif text == "スタート" and len(user_dict[id].coord) >= 2:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="検索を開始します"))
        coord_dict = {}
        for coord in user_dict[id].coord:
            coord_dict[names.get_first_name(gender=None)] = coord
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")
        opt_coord = opt_route(coord_dict, depart_str=timestamp, swarmsize=swarmsize, maxiter=maxiter)
        line_bot_api.push_message(id, TextSendMessage(text='検索がおわりました！'))
        line_bot_api.push_message(id,
                                  LocationSendMessage(title="where2meet", address="written by nayopu",
                                                      latitude=opt_coord[0], longitude=opt_coord[1]))
        user_dict[id].clear()

    elif text == "デバッグ":
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=str([user_dict[id].state, user_dict[id].coord])))

    elif text == 'ばいばい':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='さようなら'))
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='さようなら'))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't leave from 1:1 chat"))

    elif text == "キャンセル":
        user_dict[id].clear()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='はじめからやり直しましょう'))

    elif text == "Hello, world":
        text = event.message.text  # message from user
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))  # reply the same message from user
    else:
        if not user_dict[id].isexplained:
            line_bot_api.push_message(id,
                                      [TextSendMessage(text="お困りですか？"),
                                       TextSendMessage(text="[手伝って]ではじめます"),
                                       TextSendMessage(text="様子がおかしいときは[キャンセル]で"),
                                       TextSendMessage(text="用が済んだら[ばいばい]しましょう")])
            user_dict[id].isexplained = True


@handler.add(MessageEvent, message=LocationMessage)
# @consor(database)
def handle_location_message(event):
    global user_dict

    if isinstance(event.source, SourceGroup):
        id = event.source.group_id
    elif isinstance(event.source, SourceRoom):
        id = event.source.room_id
    else:
        id = event.source.user_id
    if not id in user_dict:
        user_dict[id] = UserStatus()

    if user_dict[id].state == "collecting_coordination":
        user_dict[id].coord.append([event.message.latitude, event.message.longitude])
        if len(user_dict[id].coord) == 1:
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=str(event.message.address) + "ですね！"),
                                                           TextSendMessage(text="他の人の位置情報も教えてください")])
        elif len(user_dict[id].coord) >= 2:
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=str(event.message.address) + "ですね！"),
                                                           TextSendMessage(text="他の人の位置情報も教えてください"),
                                                           TextSendMessage(text="検索を開始するときは[スタート]の合図をください")])

    else:
        user_dict[id].clear()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="最初からやり直してください"))


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=80, help='port')
    arg_parser.add_argument('-ip', '--host', type=str, default="0.0.0.0", help='host')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port, host=options.host)