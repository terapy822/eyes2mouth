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

from scipy.misc import imread, imsave, imresize
from facecrop import crop_face
from utils import resize_and_rotate

app = Flask(__name__)

token = "qKYgJNQ5STQbegfWu5WSRFOQ9bRB32wbGTCZ8h6iNQEgUMISmdmh293pqekm+OAF5fmWt4kfO68Efjd+rW1Nj03d08xYFVoecOaptmEH/PmyxPsK4Vr9Q8sKxe2NOVI1LnNpL70Z4sDlFp9yQtfJHwdB04t89/1O/w1cDnyilFU="
secret_key = "e70a2bc22458f404ece19733305f8ef7"
line_bot_api = LineBotApi(token)
handler = WebhookHandler(secret_key)

base_url = "https://nayopu.ngrok.io/"
static_tmp_path = os.path.join('static', 'tmp')
static_gen_path = os.path.join('static', 'gen')
os.makedirs(static_tmp_path, exist_ok=True)
os.makedirs(static_gen_path, exist_ok=True)

# create user stats dictionary
user_dict = {}

# get model instance
model = pix2pix(tf.Session(), dataset_name="face128", image_size=128, batch_size=1, output_size=128, checkpoint_dir="checkpoint/")

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

@handler.add(MessageEvent, message=ImageMessage)
def handle_content_message(event):
    ext = 'jpg'

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    # get path
    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)
    image_path = os.path.join(static_tmp_path, dist_name)

    img = imread(image_path)
    face_img = crop_face(img, (100, 100))
    face_img = imresize(face_img, (128, 128))
    resized_img = resize_and_rotate(face_img, 128)
    gen_img = model.test_1_image(resized_img)

    gen_path = os.path.join(static_gen_path, dist_name)
    imsave(gen_path, gen_img)

    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
        original_content_url=os.path.join(base_url, gen_path),
        preview_image_url=os.path.join(base_url, gen_path)))


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=80, help='port')
    arg_parser.add_argument('-ip', '--host', type=str, default="0.0.0.0", help='host')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port, host=options.host)