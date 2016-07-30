#!/usr/bin/env python

import time
import requests
import json
from lxml import html
from datetime import datetime
from settings import KGS_URL, ASR_CHANNEL, ASR_PLAYERS_URL, PASSWD
from model import db, ASRClass
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('ASRbot', 'templates'))

def post_kgs(data, cookies=None):
    r = requests.post(KGS_URL, json.dumps(data), cookies=cookies)
    if r.status_code != 200:
        print r.text
        exit()
    return r.cookies

def fetch_members():
    ASR = {}
    page = requests.get(ASR_PLAYERS_URL)
    tree = html.fromstring(page.content)
    for p in tree.xpath("//div[@id='room_Alpha']//a/text()"):
        ASR[p] = 'ALPHA'
    for p in tree.xpath("//div[@id='room_Beta']//a/text()"):
        ASR[p] = 'BETA'
    for p in tree.xpath("//div[@id='room_Gamma']//a/text()"):
        ASR[p] = 'GAMMA'
    for p in tree.xpath("//div[@id='room_Delta']//a/text()"):
        ASR[p] = 'DELTA'
    for p in tree.xpath("//div[@id='room_Placement_League']//a/text()"):
        ASR[p] = 'PLACEMENT'
    return ASR

db.connect()

cookies = post_kgs({
    "type": "LOGIN",
    "name": "ASRbot",
    "password": PASSWD,
    "locale": "en_US"
})

ASR = fetch_members()
done = False
present = {'ALPHA': [], 'BETA': [], 'DELTA': [], 'GAMMA': [], 'PLACEMENT': []}
available = {'ALPHA': 0, 'BETA': 0, 'DELTA': 0, 'GAMMA': 0, 'PLACEMENT': 0}
while done == False:
    time.sleep(5)
    r = requests.get(KGS_URL, cookies=cookies)
    if r.status_code != 200:
        print r.text
        exit()
    for m in json.loads(r.text)['messages']:
        if m['type'] == 'ROOM_JOIN' and m['channelId'] == ASR_CHANNEL:
            for user in m['users']:
                if user['name'] in ASR:
                    room = ASR[user['name']]
                    present[room].append("{} ({})".format(user['name'], user['flags']))
                    if 'p' in user['flags']:
                        available[room] += 1
            done = True
            break

now = datetime.utcnow()
print now
print present
template = env.get_template('index.html')
f = open('out/index.html', 'w')
f.write(template.render(now=now, present=present))
f.close()

for room in present:
    asrclass = ASRClass(name=room, 
                        date=now, 
                        present=present[room], 
                        total_nb=len(present[room]), 
                        available_nb=available[room])
    asrclass.save()

post_kgs({"type": "LOGOUT"}, cookies=cookies)
