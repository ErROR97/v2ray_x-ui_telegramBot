
# Hi, I'm Error! 👋

V2RAY x-ui Telegram BOT Panel 
====================
We Use this [repository](https://github.com/python-telegram-bot/python-telegram-bot)
 for Build TB

## Installation

You can install v2ray telegram bot via

*** Use codes in root user ***

```bash
    $ git clone https://github.com/ErROR97/v2ray_x-ui_telegramBot.git
    $ cd v2ray_x-ui_telegramBot
    $ cp port.db /etc/x-ui/
    $ pip3 install requests
    $ pip3 install schedule
    $ pip3 install PyYAML
    $ python3 setup.py install
```

## Setup config.yml:

this bot need 2 TELEGRAM BOT TOKEN
(you can create and get 2 bot from [BotFather](https://t.me/BotFather)  and get chat id from  [CidBot](https://t.me/cid_bot) )


```javascript
bot_token:
    admin: "ADMIN BOT TOKEN"
    server: "SERVER BOT TOKEN"

chat_id:
    id: "CHAT ID"
```

## Run bot 

```bash
    $ cd v2ray_x-ui_telegramBot
    $ cd examples
    $ nohup python3 admin.py
```
![Logo](https://i.postimg.cc/x1qJkwrh/bot.jpg)


## Ability


- get user list.

- get Account details(upload,download,protocol,port,transport,Expire date).

- Active Account.

- DeActive Account.

- change count of connect(set multi user config).

- Add Account(just TROJAN).

- Delete Account from DataBase.



## Features

- Add more transport configuration

