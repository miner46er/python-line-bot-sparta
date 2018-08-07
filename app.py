import os
import sys
import psycopg2
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    BubbleContainer, ImageComponent, BoxComponent, TextComponent,
    SpacerComponent, IconComponent, ButtonComponent, SeparatorComponent,
    URIAction, ButtonsTemplate, PostbackAction, MessageAction,
    TemplateSendMessage, rich_menu, imagemap, ImageCarouselTemplate,
    ImageCarouselColumn, CarouselTemplate, CarouselColumn, PostbackEvent,

)



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

BOT_PREFIX = os.getenv('BOT_PREFIX', '!')

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
    # menu list
    rice_type = os.getenv('RICE_TYPE', '').split(', ')
    topping_type = os.getenv('TOPPING_TYPE', '').split(', ')
    sauce_type = os.getenv('SAUCE_TYPE', '').split(', ')

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

        # echo command: reply arguments to user
        if command == 'echo':
            if(arguments_string != ''):
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=arguments_string)
                )

        elif command == 'flex':
            bubble = BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url='https://img.wongnai.com/p/1920x0/2017/12/30/19f2934940cf47669b2d1336feea0b97.jpg',
                    size='full',
                    aspect_ratio='4:3',
                    aspect_mode='cover',
                    action=URIAction(uri='https://github.com/miner46er/python-line-bot-sparta', label='label')
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        # title
                        TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                        # review
                        BoxComponent(
                            layout='baseline',
                            margin='md',
                            contents=[
                                IconComponent(size='sm', url='https://cdn2.iconfinder.com/data/icons/default-1/100/.svg-4-512.png'),
                                IconComponent(size='sm', url='https://freeiconshop.com/wp-content/uploads/edd/star-curved-outline.png'),
                                IconComponent(size='sm', url='https://cdn2.iconfinder.com/data/icons/default-1/100/.svg-4-512.png'),
                                IconComponent(size='sm', url='https://cdn2.iconfinder.com/data/icons/default-1/100/.svg-4-512.png'),
                                IconComponent(size='sm', url='https://freeiconshop.com/wp-content/uploads/edd/star-curved-outline.png'),
                                TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                              flex=0)
                            ]
                        ),
                        # info
                        BoxComponent(
                            layout='vertical',
                            margin='lg',
                            spacing='sm',
                            contents=[
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Place',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text='Shinjuku, Tokyo',
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
                                    ],
                                ),
                                BoxComponent(
                                    layout='baseline',
                                    spacing='sm',
                                    contents=[
                                        TextComponent(
                                            text='Time',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=1
                                        ),
                                        TextComponent(
                                            text="10:00 - 23:00",
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5,
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        # callAction, separator, websiteAction
                        SpacerComponent(size='sm'),
                        # callAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(label='CALL', uri='tel:000000'),
                        ),
                        # separator
                        SeparatorComponent(),
                        # websiteAction
                        ButtonComponent(
                            style='link',
                            height='sm',
                            action=URIAction(label='WEBSITE', uri="https://github.com/miner46er/python-line-bot-sparta")
                        )
                    ]
                ),
            )
            message = FlexSendMessage(alt_text="hello", contents=bubble)
            line_bot_api.reply_message(
                event.reply_token,
                message
            )
        
        elif command == 'buttons':
            buttons_template = ButtonsTemplate(
                title='My buttons sample', text='Hello, my buttons', actions=[
                    URIAction(label='Go to line.me', uri='https://line.me'),
                    PostbackAction(label='ping', data='ping'),
                    PostbackAction(label='ping with text', data='ping', text='ping'),
                    MessageAction(label='Translate Rice', text='米')
                ])
            menu_pesan = TemplateSendMessage(
                alt_text='Buttons alt text', template=buttons_template)

            line_bot_api.reply_message(event.reply_token, menu_pesan)
        
        elif command == 'pesan':
            if len(arguments_list) == 0:
                pilihan_menu = ImageCarouselTemplate(columns=[
                    ImageCarouselColumn(
                        image_url='https://via.placeholder.com/512x512',
                        action=MessageAction(label='Nasi Putih', text=BOT_PREFIX + command + arguments_string + ' putih')
                        ),
                    ImageCarouselColumn(
                        image_url='https://via.placeholder.com/512x512',
                        action=MessageAction(label='Nasi Umami', text=BOT_PREFIX + command + arguments_string + ' umami')
                        )
                ])
                menu_pesan = TemplateSendMessage(
                    alt_text='Menu pesanan', template=pilihan_menu)
                
                line_bot_api.reply_message(event.reply_token, menu_pesan)
            
            elif len(arguments_list) == 1:
                if rice_type.count(arguments_list[0]) == 1:
                    pilihan_menu = ImageCarouselTemplate(columns=[
                        ImageCarouselColumn(
                            image_url='https://via.placeholder.com/512x512',
                            action=MessageAction(label='Ayam', text=BOT_PREFIX + command + ' ' + arguments_string + ' ayam')
                            ),
                        ImageCarouselColumn(
                            image_url='https://via.placeholder.com/512x512',
                            action=MessageAction(label='Cumi', text=BOT_PREFIX + command + ' ' + arguments_string + ' cumi')
                            ),
                        ImageCarouselColumn(
                            image_url='https://via.placeholder.com/512x512',
                            action=MessageAction(label='Campur', text=BOT_PREFIX + command + ' ' + arguments_string + ' campur')
                            )
                    ])
                    menu_pesan = TemplateSendMessage(
                        alt_text='Menu pesanan', template=pilihan_menu)
                    
                    line_bot_api.reply_message(event.reply_token, menu_pesan)

                else:
                    order_mistake(event)


            elif 2 <= len(arguments_list) <= 5:
                if (rice_type.count(arguments_list[0]) == 1) and (topping_type.count(arguments_list[1]) == 1):
                    '''pilihan_menu = ImageCarouselTemplate(columns=[
                        ImageCarouselColumn(
                            image_url='https://via.placeholder.com/512x512',
                            action=MessageAction(label='XO', text=BOT_PREFIX + command + ' ' + arguments_string + ' xo')
                            ),
                        ImageCarouselColumn(
                            image_url='https://via.placeholder.com/512x512',
                            action=MessageAction(label='Mayonnaise', text=BOT_PREFIX + command + ' ' + arguments_string + ' mayo')
                            ),
                        ImageCarouselColumn(
                            image_url='https://via.placeholder.com/512x512',
                            action=MessageAction(label='Bumbu Bali', text=BOT_PREFIX + command + ' ' + arguments_string + ' bali')
                            ),
                        ImageCarouselColumn(
                            image_url='https://via.placeholder.com/512x512',
                            action=MessageAction(label='Blackpepper', text=BOT_PREFIX + command + ' ' + arguments_string + ' blackpepper')
                            )
                    ])
                    menu_pesan = TemplateSendMessage(
                        alt_text='Menu pesanan', template=pilihan_menu)'''
                    
                    summary_button = ButtonsTemplate(
                        title='Pesananmu sekarangNasi: ' + arguments_list[0] + 'Topping: ' + arguments_list[1] + 'Saus: ', actions=[
                            MessageAction(label='Selesai memesan', text=BOT_PREFIX + command + ' ' + arguments_string + ' selesai')
                        ])
                    order_summary = TemplateSendMessage(
                        alt_text='Pesanan saat ini', template=summary_button)

                    line_bot_api.reply_message(event.reply_token, order_summary)
            else:
                order_mistake(event)

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