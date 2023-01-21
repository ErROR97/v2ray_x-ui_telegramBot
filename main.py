from glob import glob
import os;
import sqlite3;
import time;
import requests;
import subprocess;
import threading;
import schedule;
_db_address = '/etc/x-ui/x-ui.db'
_db_ports_address = '/etc/x-ui/port.db'
_user_last_id = 0
_telegrambot_token = ''
_telegram_chat_id = ' ' # you can get this in @cid_bot bot.

def getUsers():
    global _user_last_id
    conn = sqlite3.connect(_db_address)
    cursor = conn.execute(f"select id,remark,port from inbounds where id > {_user_last_id}");
    users_list = [];
    for c in cursor:
        users_list.append({'name':c[1],'port':c[2]})
        _user_last_id = c[0];
    conn.close();
    return users_list

def get_user_ports():
    conn = sqlite3.connect(_db_ports_address)
    cursor = conn.execute(f"select port,count from ports");
    users_port = [];
    for c in cursor:
        users_port.append({'port':c[0],'count':c[1]})
    conn.close();
    return users_port

def get_count():
    conn = sqlite3.connect(_db_ports_address)
    cursor = conn.execute(f"select port,count from ports");
    users_port = [];
    for c in cursor:
        users_port.append({'port':c[0],'count':c[1]})
    conn.close();
    return users_port

def disableAccount(user_port):
    conn = sqlite3.connect(_db_address) 
    conn.execute(f"update inbounds set enable = 0 where port={user_port}");
    conn.commit()
    conn.close();
    time.sleep(2)
    os.popen("x-ui restart")
    time.sleep(3)
    
def checkNewUsers():
    conn = sqlite3.connect(_db_address)
    cursor = conn.execute(f"select count(*) from inbounds WHERE id > {_user_last_id}");
    new_counts = cursor.fetchone()[0];
    conn.close();
    if new_counts > 0:
        init()

def init():
    global _telegram_chat_id
    global _telegrambot_token
    cfg = " "
    with open("python-telegram-bot/config.yml", "r") as ymlfile: cfg = yaml.load(ymlfile)
    _telegrambot_token = str(cfg["bot_token"]["server"])
    _telegram_chat_id = int(cfg["chat_id"]["id"])

    users_list = getUsers();
    user_ports = get_user_ports()
    for row in user_ports:
        print("port:",row['port']," count:",row['count'])
        for user in users_list:
            if row['port'] == user['port']:
                thread = AccessChecker(user,row['count'])
                thread.start()

class AccessChecker(threading.Thread):
    def __init__(self, user,count):
        threading.Thread.__init__(self)
        self.user = user;
        self.count = count
    def run(self):
        user_remark = self.user['name'];
        user_port = self.user['port'];
        count = self.count
        while True:
            netstate_data =  os.popen("netstat -np 2>/dev/null | grep :"+str(user_port)+" | awk '{if($3!=0) print $5;}' | cut -d: -f1 | sort | uniq -c | sort -nr | head").read();
            netstate_data = str(netstate_data)
            connection_count =  len(netstate_data.split("\n")) - 1;
            #print("c "+str(user_port) + "-"+ str(connection_count)+ " - " + str(count))

            if connection_count > count:
                msg = "✔️ User: " + user_remark + " ===> DeActivated (count:)" + str(count) + " 🔒" 
                requests.get(f'https://api.telegram.org/bot{_telegrambot_token}/sendMessage?chat_id={_telegram_chat_id}&text={msg}')
                disableAccount(user_port=user_port)
                print(f"inbound with port {user_port} blocked")
            else:
                time.sleep(2)

init();
schedule.every(10).minutes.do(checkNewUsers)
while True:
    schedule.run_pending()
    time.sleep(1)
