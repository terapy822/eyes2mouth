# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from argparse import ArgumentParser
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, LocationMessage, LocationSendMessage, SourceGroup, SourceRoom, ImageMessage, ImageSendMessage
from model import pix2pix
import tensorflow as tf
import tempfile
import numpy as np
from scipy.misc import imread, imsave, imresize
from facecrop import crop_face
from utils import resize_and_rotate, crop_ratio_2to1
import numpy as np

app = Flask(__name__)

token = "qKYgJNQ5STQbegfWu5WSRFOQ9bRB32wbGTCZ8h6iNQEgUMISmdmh293pqekm+OAF5fmWt4kfO68Efjd+rW1Nj03d08xYFVoecOaptmEH/PmyxPsK4Vr9Q8sKxe2NOVI1LnNpL70Z4sDlFp9yQtfJHwdB04t89/1O/w1cDnyilFU="
secret_key = "e70a2bc22458f404ece19733305f8ef7"
line_bot_api = LineBotApi(token)
handler = WebhookHandler(secret_key)

base_url = "https://nayopu.ngrok.io/"
static_tmp_dir = os.path.join('static', 'tmp')
static_gen_dir = os.path.join('static', 'gen')
static_crop_dir = os.path.join('static', 'crop')
os.makedirs(static_tmp_dir, exist_ok=True)
os.makedirs(static_gen_dir, exist_ok=True)
os.makedirs(static_crop_dir, exist_ok=True)

# create user stats dictionary
user_dict = {}

image_size = 128

hatena_img = imresize(imread("hatena.jpg"), (int(image_size/2), image_size))

batch_imgs = np.load("batch.npy")

# get model instance
model = pix2pix(tf.Session(), dataset_name="face128", image_size=image_size, batch_size=10, output_size=128, checkpoint_dir="checkpoint/")
assert model.load(model.checkpoint_dir), " [-] Load FAILED"
print(" [*] Load SUCCESS")

class UserStatus():
    def __init__(self):
        self.state = "waiting"
        self.name = ""

    def clear(self):
        self.state = "waiting"
        self.name = ""


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
    text = event.message.text
    if isinstance(event.source, SourceGroup):
        id = event.source.group_id
    elif isinstance(event.source, SourceRoom):
        id = event.source.room_id
    else:
        id = event.source.user_id
    if id in user_dict:
        if text == "はい" and user_dict[id].state == "pending":
            dist_name = user_dict[id].name
            face_img = imread(os.path.join(static_crop_dir, dist_name))
            resized_img = resize_and_rotate(face_img, image_size)
            gen_img = model.test_1_image(resized_img, batch_imgs)
            gen_path = os.path.join(static_gen_dir, dist_name)
            imsave(gen_path, gen_img)
            line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=os.path.join(base_url, gen_path),
                                                         preview_image_url=os.path.join(base_url, gen_path)))
            user_dict[id].clear()

        elif text == "いいえ" and user_dict[id].state == "pending":
            user_dict[id].clear()
            line_bot_api.reply_message(event.reply_token, TextSendMessage("最初からやりなおしてください"))
        else:
            return
    else:
        return

@handler.add(MessageEvent, message=ImageMessage)
def handle_content_message(event):
    if isinstance(event.source, SourceGroup):
        id = event.source.group_id
    elif isinstance(event.source, SourceRoom):
        id = event.source.room_id
    else:
        id = event.source.user_id
    if not id in user_dict:
        user_dict[id] = UserStatus()
    ext = "jpg"
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_dir, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    # get path
    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)
    image_path = os.path.join(static_tmp_dir, dist_name)

    img = imread(image_path)

    if user_dict[id].state == "waiting":
        face_img = crop_face(img, (image_size, image_size))
        if np.isnan(face_img).any():
            line_bot_api.reply_message(event.reply_token,
                                       [TextSendMessage("顔をみつけられませんでした"),
                                        TextSendMessage("切り出した画像をおくってください")])
            user_dict[id].state = "crop_pending"
        else:
            # face_img = imresize(face_img, (128, 128))
            eyes_img = face_img[:int(image_size/2), :, :]
            concat_img = np.concatenate([eyes_img, hatena_img], axis=0)
            img_path = os.path.join(static_crop_dir, dist_name)
            imsave(img_path, concat_img)
            line_bot_api.reply_message(event.reply_token,
                                       [ImageSendMessage(original_content_url=os.path.join(base_url, img_path), preview_image_url=os.path.join(base_url, img_path)),
                                        TextSendMessage("心のじゅんびはよろしいですか？"),
                                        TextSendMessage("はい / いいえ")])
            user_dict[id].name = dist_name
            user_dict[id].state = "pending"
    elif user_dict[id].state == "crop_pending":
        eyes_img = imresize(crop_ratio_2to1(img), (int(image_size/2), image_size))
        concat_img = np.concatenate([eyes_img, hatena_img], axis=0)
        img_path = os.path.join(static_crop_dir, dist_name)
        imsave(img_path, concat_img)
        line_bot_api.reply_message(event.reply_token,
                                   [ImageSendMessage(original_content_url=os.path.join(base_url, img_path), preview_image_url=os.path.join(base_url, img_path)),
                                    TextSendMessage("心のじゅんびはよろしいですか？"),
                                    TextSendMessage("はい / いいえ")])
        user_dict[id].name = dist_name
        user_dict[id].state = "pending"

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=80, help='port')
    arg_parser.add_argument('-ip', '--host', type=str, default="0.0.0.0", help='host')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port, host=options.host)