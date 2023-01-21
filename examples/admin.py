import logging

from glob import glob
import os;
import sqlite3;
import time;
import math
import random
import secrets
import string
import json
import subprocess
import yaml


from telegram import __version__ as TG_VER
from telegram import ForceReply, Update

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

SELECTED,ACCOUNT_DETAILS, ACTIVE, DEACTIVE, USERLIST, DELETE, ADD, CHANGECOUNT = range(8)
_db_address = '/etc/x-ui//x-ui.db'
_db_address2 = '/etc/x-ui/port.db'
chat_id = 0

def find_pid_from_name(cmd_name,prosses_name):
    pid_list = " "
    p = subprocess.Popen('pidof ' + cmd_name + " " + prosses_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        line = str(line)
        line = line[2:]
        line = line[:len(line) -3]
        pid_list = line.split(" ")
    p.wait()
    bot_pid = " "
    for pid in pid_list:
        cmd = "ps aux | grep " + str(pid)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            line = str(line)
            line = line[2:]
            line = line[:len(line) -3]
            find = line.find(prosses_name)
            if find > 0:
                bot_pid = pid

        p.wait()

    return(bot_pid)

def run_filter_port():
    p = find_pid_from_name("python3","main.py")
    os.popen("kill " + p)
    os.popen("nohup python3 /python-telegram-bot/main.py")


def create_port_manager_db():
    conn = sqlite3.connect(_db_address2) 
    c = conn.cursor()
    c.execute('''
          CREATE TABLE IF NOT EXISTS ports
          ([port_id] INTEGER PRIMARY KEY, [port] INTEGER,[count] INTEGER)
          ''')
    conn.commit()

def insert_ports(count):
    count = "'" + str(count) + "'"
    conn = sqlite3.connect(_db_address2)
    c = conn.cursor()
    c.execute('DELETE FROM ports;',);
    conn.commit()

    users = get_users_list()
    for user in users:
        port = user["port"]
        conn.execute(f"INSERT INTO ports (port,count)VALUES({port},{count})")
        conn.commit()

    run_filter_port()
    
def update_port_count(port,count):
    conn = sqlite3.connect(_db_address2) 
    conn.execute(f"update ports set count = {count} where port={port}");
    conn.commit()
    conn.close();
    time.sleep(2)

    run_filter_port()

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def enableAccount(user_port):
    conn = sqlite3.connect(_db_address) 
    conn.execute(f"update inbounds set enable = 1 where port={user_port}");
    conn.commit()
    conn.close();
    time.sleep(2)
    os.popen("x-ui restart")
    time.sleep(3)

def find_count(port):
    port = "'" + port + "'"
    conn = sqlite3.connect(_db_address2)
    cursor = conn.execute(f"select count from ports where port = {port}");
    user_ditails = [];
    for c in cursor:
        user_ditails.append({'count':c[0]})
    conn.close();
    return user_ditails

def disableAccount(user_port):
    conn = sqlite3.connect(_db_address) 
    conn.execute(f"update inbounds set enable = 0 where port={user_port}");
    conn.commit()
    conn.close();
    time.sleep(2)
    os.popen("x-ui restart")
    time.sleep(3)

def get_users_ditals(user_name):
    user_name = "'" + user_name + "'"
    conn = sqlite3.connect(_db_address)
    cursor = conn.execute(f"select * from inbounds where remark = {user_name}");
    user_ditails = [];
    for c in cursor:
        print("data:",len(c))
        user_ditails.append({'id':c[0],'user_id':c[1],'upload':c[2],'download':c[3],'total':c[4],'remark':c[5],'enable':c[6],'expiry_time':c[7],'listen':c[8],'port':c[9],'protocol':c[10],'settings':c[11],'stream_settings':c[12],'tag':c[13],'sniffing':c[14]})

    conn.close();
    return user_ditails

def user_list_text(user_ditails,list_user):
    for user_v2ray_ditals in user_ditails:
        list_user += str(user_v2ray_ditals['remark'])
        list_user += '\n'
    
    return list_user

def get_users_list():
    conn = sqlite3.connect(_db_address)
    cursor = conn.execute(f"select * from inbounds where id > 0");
    user_ditails = [];
    for c in cursor:
        user_ditails.append({'id':c[0],'user_id':c[1],'upload':c[2],'download':c[3],'total':c[4],'remark':c[5],'enable':c[6],'expiry_time':c[7],'listen':c[8],'port':c[9],'protocol':c[10],'settings':c[11],'stream_settings':c[12],'tag':c[13],'sniffing':c[14]})

    conn.close();
    return user_ditails

def add_acc_db(username,user_port,protocol,setting,stream_settings,tag,sniffing):
    conn = sqlite3.connect(_db_address)
    username = "'" + username + "'"
    user_port = "'" + str(user_port) + "'"
    protocol = "'" + protocol + "'"
    setting = "'" + setting + "'"
    stream_settings = "'" + stream_settings + "'"
    tag = "'" + tag + "'"
    sniffing = "'" + sniffing + "'"
    conn.execute(f"INSERT INTO inbounds (user_id,up,down,total,remark,enable,expiry_time,listen,port,protocol,settings,stream_settings,tag,sniffing)VALUES(1,0,0,0,{username},1,0,' ',{user_port},{protocol},{setting},{stream_settings},{tag},{sniffing});");
    conn.commit()
    conn.close();
    time.sleep(2)
    os.popen("x-ui restart")
    time.sleep(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["User List","Account Details", "Active", "Deactive"],["Change Count of Connect"],["Add Account","Delete Account"]]

    await update.message.reply_text(
        "V2Ray VPN",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select From keyboard",
        ),
    )

    return SELECTED

async def selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("selected")
    
    if update.message.chat.id == chat_id:

        msg_send = update.message.text
        if msg_send == "Account Details":
            await update.message.reply_text(
                "enter your username:"
            )
            return ACCOUNT_DETAILS
        
        elif msg_send == "Active":
            await update.message.reply_text(
                "enter your username:"
            )
            return ACTIVE

        elif msg_send == "Deactive":
            await update.message.reply_text(
                "enter your username:"
            )
            return DEACTIVE

        elif msg_send == "User List":
            list_user = user_list_text(get_users_list()," ")
            count = len(get_users_list())
            msg = "count = " + str(count) 
            msg += '\n'
            msg += list_user
            await update.message.reply_text(
                msg
            )
            return SELECTED

        elif msg_send == "Delete Account":
            
            await update.message.reply_text(
                "enter your username:"
            )
            return DELETE

        elif msg_send == "Add Account":
            await update.message.reply_text(
                "enter your username:"
            )
            return ADD
        
        elif msg_send == "Change Count of Connect":
            await update.message.reply_text(
                "enter your username and count (example: test 2):"
            )
            return CHANGECOUNT

async def delete_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    massage_to_send = "sory you are not admin!"
    print("delete_account")
    if update.message.chat.id == chat_id:
        username = update.message.text
        user_v2ray_ditals = get_users_ditals(username)
        if len(user_v2ray_ditals) != 0:
            delete_acc_db(username)
            insert_ports(2)
            massage_to_send = "✔️ User: " + username + " ===> Deleted 🗑"
        else :
            massage_to_send = "✔️ " + username +  " ===> not found! 🔍"


    await update.message.reply_text(
        massage_to_send
    )

    reply_keyboard = [["User List","Account Details", "Active", "Deactive"],["Change Count of Connect"],["Add Account","Delete Account"]]

    await update.message.reply_text(
        "V2Ray VPN",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select From keyboard"
        ),
    )

    return SELECTED

async def add_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    massage_to_send = "sory you are not admin!"
    print("add_account")
    if update.message.chat.id == chat_id:
        username = update.message.text
        user_v2ray_ditals = get_users_ditals(username)
        if len(user_v2ray_ditals) != 0:
            massage_to_send = "✔️ " + username +  " ===> Faild(Exist User) ❗️"
            
        else :
            massage_to_send = "✔️ User: " + username + " ===> Added 📥"
            v2ray_user_list = get_users_list()
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(20))
            protocol = "trojan"
            user_port = random.randrange(10000, 90000)
            cert = "/root/cert.crt"
            keyFile = "/root/private.key"
            setting = json.dumps({
                "clients": [{'password': password, 'flow': 'xtls-rprx-direct'}],
                "fallbacks": []
                })
            
            stream_settings = json.dumps({
                "network": "tcp",
                "security": "xtls",
                "xtlsSettings": {
                    "serverName": "",
                    "certificates": [{"certificateFile": cert,"keyFile": keyFile}]
                },"tcpSettings": {"header": {"type": "none"}}
            })
            sniffing = json.dumps({"enabled": "true","destOverride": ["http", "tls"]})

            for user in v2ray_user_list:
                if user["port"] != user_port:
                    tag = f"trojan-{user_port}"

                    print("remark:",username," port:",user_port," protocol:",protocol)
                    print("settings:",setting)
                    print("stream_settings:",stream_settings)
                    print("tag:",tag)
                    print("sniffing:",sniffing)
                    break
            add_acc_db(username,user_port,protocol,setting,stream_settings,tag,sniffing)
            insert_ports(2)
            


    await update.message.reply_text(
        massage_to_send
    )

    reply_keyboard = [["User List","Account Details", "Active", "Deactive"],["Change Count of Connect"],["Add Account","Delete Account"]]
    await update.message.reply_text(
        "V2Ray VPN",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select From keyboard"
        ),
    )

    return SELECTED

async def account_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    massage_to_send = "sory you are not admin!"
    print("account_details")
    if update.message.chat.id == chat_id:
        username = update.message.text
        user_v2ray_ditals = get_users_ditals(username)
        upload = str(convert_size(user_v2ray_ditals[0]['upload']))
        download = str(convert_size(user_v2ray_ditals[0]['download']))
        enable = str(user_v2ray_ditals[0]['enable'])
        expiry_time = str(user_v2ray_ditals[0]['expiry_time'])
        port = str(user_v2ray_ditals[0]['port'])
        protocol = str(user_v2ray_ditals[0]['protocol'])
        count = str(find_count(port)[0]["count"])

        massage_to_send = f"username =  {username} \n"
        massage_to_send = massage_to_send + f"upload = {upload} \n"
        massage_to_send = massage_to_send + f"download = {download} \n"
        massage_to_send = massage_to_send + f"enable = {enable} \n"
        massage_to_send = massage_to_send + f"expiry_time = {expiry_time} \n"
        massage_to_send = massage_to_send + f"port = {port} \n"
        massage_to_send = massage_to_send + f"count = {count} \n"
        massage_to_send = massage_to_send + f"protocol = {protocol} \n"

    await update.message.reply_html(
        massage_to_send,
        reply_markup=ForceReply(selective=True),
    )

    reply_keyboard = [["User List","Account Details", "Active", "Deactive"],["Change Count of Connect"],["Add Account","Delete Account"]]
    await update.message.reply_text(
        "V2Ray VPN",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select From keyboard"
        ),
    )

    return SELECTED

async def active_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    massage_to_send = "sory you are not admin!"
    print("active_account")
    if update.message.chat.id == chat_id:
        username = update.message.text
        user_v2ray_ditals = get_users_ditals(username)
        if len(user_v2ray_ditals) != 0:
            enableAccount(user_v2ray_ditals[0]['port'])
            massage_to_send = "✔️ User: " + username + " ===> Activated 🔓"
        else :
            massage_to_send = "✔️ " + username +  " ===> not found! 🔍"


    await update.message.reply_text(
        massage_to_send
    )

    reply_keyboard = [["User List","Account Details", "Active", "Deactive"],["Change Count of Connect"],["Add Account","Delete Account"]]
    await update.message.reply_text(
        "V2Ray VPN",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select From keyboard"
        ),
    )

    return SELECTED

async def deactive_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    massage_to_send = "sory you are not admin!"
    print("deactive_account")
    if update.message.chat.id == chat_id:
        username = update.message.text
        user_v2ray_ditals = get_users_ditals(username)
        if len(user_v2ray_ditals) != 0:
            disableAccount(user_v2ray_ditals[0]['port'])
            massage_to_send = "✔️ User: " + username + " ===> DeActivated 🔒"
        else :
            massage_to_send = "✔️ " + username +  " ===> not found! 🔍"


    await update.message.reply_text(
        massage_to_send
    )

    reply_keyboard = [["User List","Account Details", "Active", "Deactive"],["Change Count of Connect"],["Add Account","Delete Account"]]
    await update.message.reply_text(
        "V2Ray VPN",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select From keyboard"
        ),
    )

    return SELECTED

async def change_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    massage_to_send = "sory you are not admin!"
    print("change_count")
    if update.message.chat.id == chat_id:
        text = update.message.text
        index = text.rfind(" ")
        username = text[:index]
        count = text[index + 1:]
        user_v2ray_ditals = get_users_ditals(username)
        if len(user_v2ray_ditals) != 0:
            print(username)
            print(count)
            update_port_count(user_v2ray_ditals[0]['port'],count)
            massage_to_send = "✔️ User: " + username + " ===> Changed Count Of Connect to: " + str(count)
        else :
            massage_to_send = "✔️ " + username +  " ===> not found! 🔍"


    await update.message.reply_text(
        massage_to_send
    )

    reply_keyboard = [["User List","Account Details", "Active", "Deactive"],["Change Count of Connect"],["Add Account","Delete Account"]]
    await update.message.reply_text(
        "V2Ray VPN",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select From keyboard"
        ),
    )

    return SELECTED

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    global chat_id
    cfg = " "
    with open("python-telegram-bot/config.yml", "r") as ymlfile: cfg = yaml.load(ymlfile)
    token = str(cfg["bot_token"]["admin"])
    chat_id = int(cfg["chat_id"]["id"])

    create_port_manager_db()
    insert_ports(2)

    application = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTED: [MessageHandler(filters.Regex("^(User List|Account Details|Active|Deactive|Delete Account|Add Account|Change Count of Connect)$"), selected)],
            ACCOUNT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, account_details)],
            ACTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, active_account)],
            DEACTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, deactive_account)],
            CHANGECOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_count)],
            DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_account)],
            ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_account)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()
