import os
import sys
import psycopg2
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    BubbleContainer, ImageComponent, BoxComponent, TextComponent,
    SpacerComponent, IconComponent, ButtonComponent, SeparatorComponent,
    URIAction, ButtonsTemplate, PostbackAction, MessageAction,
    TemplateSendMessage, rich_menu, imagemap, ImageCarouselTemplate,
    ImageCarouselColumn, CarouselTemplate, CarouselColumn, PostbackEvent
)

base_url = os.getenv('BASE_URL', None)

statics_url = base_url + '/static'

DATABASE_URL = os.getenv('DATABASE_URL', None)

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('CHANNEL_SECRET', None)
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# bot prefix
BOT_PREFIX = os.getenv('BOT_PREFIX', '!')

# menu list
RICE_TYPE = [x.strip() for x in os.getenv('RICE_TYPE', '').split(';')]
TOPPING_TYPE = [x.strip() for x in os.getenv('TOPPING_TYPE', '').split(';')]
SAUCE_TYPE = [x.strip() for x in os.getenv('SAUCE_TYPE', '').split(';')]

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    # check bot prefix
    if event.message.text.startswith(BOT_PREFIX):
        # seperate message contents as command and arguments
        message_body = event.message.text.strip()[1:].split()
        command = message_body[0]
        if(len(message_body) >= 2):
            arguments_list = message_body[1:]
            arguments_string = ' '.join(arguments_list)
        else:
            arguments_list = []
            arguments_string = ''

        if command == 'pesan':
            order_memo = BOT_PREFIX + command + ' ' + arguments_string
            if len(arguments_list) == 0:
                pilihan_menu = ImageCarouselTemplate(columns=[
                    ImageCarouselColumn(
                        image_url=statics_url + '/nasi_putih.jpg',
                        action=MessageAction(label='Nasi Putih', text=BOT_PREFIX + command + ' putih')
                        ),
                    ImageCarouselColumn(
                        image_url=statics_url + '/nasi_umami.jpg',
                        action=MessageAction(label='Nasi Umami', text=BOT_PREFIX + command + ' umami')
                        )
                ])
                menu_pesan = TemplateSendMessage(
                    alt_text='Menu pesanan', template=pilihan_menu)
                
                line_bot_api.reply_message(event.reply_token, menu_pesan)
            
            elif len(arguments_list) == 1:
                if RICE_TYPE.count(arguments_list[0]) == 1:
                    pilihan_menu = ImageCarouselTemplate(columns=[
                        ImageCarouselColumn(
                            image_url=statics_url + '/topping_ayam.jpg',
                            action=MessageAction(label='Ayam', text=order_memo + ' ayam')
                            ),
                        ImageCarouselColumn(
                            image_url=statics_url + '/topping_cumi.jpg',
                            action=MessageAction(label='Cumi', text=order_memo + ' cumi')
                            ),
                        ImageCarouselColumn(
                            image_url=statics_url + '/topping_campur.jpg',
                            action=MessageAction(label='Campur', text=order_memo + ' campur')
                            )
                    ])
                    menu_pesan = TemplateSendMessage(
                        alt_text='Menu pesanan', template=pilihan_menu)
                    
                    line_bot_api.reply_message(event.reply_token, menu_pesan)

                else:
                    order_mistake(event)

            elif 2 <= len(arguments_list) <= 5 and arguments_list[-1] != 'selesai':
                if validate_order(arguments_list, -1):
                    sauce_template = ImageCarouselTemplate(columns=[
                        ImageCarouselColumn(
                            image_url=statics_url + '/sauce_xo.jpg',
                            action=MessageAction(label='XO', text=order_memo + ' xo')
                            ),
                        ImageCarouselColumn(
                            image_url=statics_url + '/sauce_mayo.jpg',
                            action=MessageAction(label='Mayonnaise', text=order_memo + ' mayo')
                            ),
                        ImageCarouselColumn(
                            image_url=statics_url + '/sauce_bali.jpg',
                            action=MessageAction(label='Bumbu Bali', text=order_memo + ' bali')
                            ),
                        ImageCarouselColumn(
                            image_url=statics_url + '/sauce_blackpepper.jpg',
                            action=MessageAction(label='Blackpepper', text=order_memo + ' blackpepper')
                            )
                    ])
                    sauce_choice = TemplateSendMessage(
                        alt_text='Menu saus', template=sauce_template)
                    
                    confirm_button = ButtonsTemplate(
                        text=('Pesananmu sekarang:' +
                            '\nNasi       : ' + arguments_list[0] +
                            '\nTopping    : ' + arguments_list[1] +
                            '\nSaus(max 4): ' + ', '.join(arguments_list[2:])),
                        actions=[
                            MessageAction(label='Selesai memesan', text=order_memo + ' selesai')
                        ])
                    order_confirm = TemplateSendMessage(
                        alt_text='Pesanan saat ini', template=confirm_button)

                    line_bot_api.reply_message(event.reply_token, [sauce_choice, order_confirm])
                
                else:
                    order_mistake(event)

            elif (len(arguments_list) == 6) and (arguments_list[-1] != 'selesai'):
                if validate_order(arguments_list, -1):
                    summary_button = ButtonsTemplate(
                        text=('Apakah pesanan sudah benar?' +
                            '\nNasi       : ' + arguments_list[0] +
                            '\nTopping    : ' + arguments_list[1] +
                            '\nSaus(max 4): ' + ', '.join(arguments_list[2:])),
                        actions=[
                            MessageAction(label='Selesai memesan', text=order_memo + ' selesai')
                        ])
                    order_summary = TemplateSendMessage(
                        alt_text='Konfirmasi pesanan', template=summary_button)

                    line_bot_api.reply_message(event.reply_token, order_summary)

            elif len(arguments_list) >= 3 and arguments_list[-1] == 'selesai':
                if validate_order(arguments_list, -2):
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='Pesanan dikirim!')
                    )
                else:
                    order_mistake(event)

            else:
                order_mistake(event)

def pesanan_selesai(user_id):
    line_bot_api.push_message(
        user_id,
        TextSendMessage(text='Pesanan anda sudah dapat diambil!')
    )

def validate_order(arguments_list, last_index):
    if ((RICE_TYPE.count(arguments_list[0]) == 1) and
    (TOPPING_TYPE.count(arguments_list[1]) == 1) and
    ([SAUCE_TYPE.count(x) for x in arguments_list[2:last_index]].count(0) == 0)):
        return True
    else:
        return False


def order_mistake(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Format pesanan salah!")
    )

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)