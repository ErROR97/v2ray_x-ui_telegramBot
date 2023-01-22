..
    Make sure to apply any changes to this file to README_RAW.rst as well!
Telegram V2RAY x-ui Telegram BOT Pannel 
====================
We use [repositorie](https://github.com/python-telegram-bot/python-telegram-bot/). for and bilding this robot

Installing 
==========

You can install v2ray telegram bot via
*** Use codes in root user ***

.. code:: shell
    $ git https://github.com/ErROR97/v2ray_x-ui_telegramBot.git
    $ cd v2ray_x-ui_telegramBot
    $ cp port.db /etc/x-ui/
    $ pip3 install requests
    $ pip3 install schedule
    $ pip3 install schedule
    $ pip3 install PyYAML
    $ python3 setup.py install
    $ cd examples
    $ nohup python3 admin.py

Run bot 
==========
for this bot you are need 2 TELEGRAM BOT TOKEN
(you can create and get 2 bot from https://t.me/BotFather and get chat id from https://t.me/cid_bot)

Setup config.yml:

bot_token:
    admin: "ADMIN BOT TOKEN"
    server: "SERVER BOT TOKEN"

chat_id:
    id: "CHAT ID"

.. code:: shell
    $ cd v2ray_x-ui_telegramBot
    $ cd examples
    $ nohup python3 admin.py

==========

.. image:: https://i.postimg.cc/x1qJkwrh/bot.jpg
   :align: center
   :alt: v2ray-telegram-bot