# python-line-bot-sparta

## Getting started local env

```
$ export CHANNEL_SECRET=YOUR_LINE_CHANNEL_SECRET
$ export CHANNEL_ACCESS_TOKEN=YOUR_LINE_CHANNEL_ACCESS_TOKEN

$ pip install -r requirements.txt
```

Run the bot

```
$ python app.py
```

## Getting started with Heroku

### Heroku button

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/miner46er/python-line-bot-sparta)

then set Line bot Webhook URL: `https://{YOUR_APP}.herokuapp.com/callback`

define CHANNEL_SECRET and CHANNEL_ACCESS_TOKEN in config vars

### deploy by yourself

```sh
heroku create
heroku info # then set Line bot Webhook URL to: https://{YOUR_APP}.herokuapp.com/callback
heroku config:set LINE_CHANNEL_SECRET="..."
heroku config:set LINE_CHANNEL_ACCESS_TOKEN="..."
git push heroku master
heroku logs
```