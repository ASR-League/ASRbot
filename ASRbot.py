#!/usr/bin/env python

import time
import requests
import json
from lxml import html
from datetime import datetime
from settings import KGS_URL, ASR_CHANNEL, ASR_PLAYERS_URL, PASSWD

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

cookies = post_kgs({
    "type": "LOGIN",
    "name": "ASRbot",
    "password": PASSWD,
    "locale": "en_US"
})

ASR = fetch_members()
done = False
present = {'ALPHA': [], 'BETA': [], 'DELTA': [], 'GAMMA': [], 'PLACEMENT': []}
while done == False:
    time.sleep(5)
    r = requests.get(KGS_URL, cookies=cookies)
    if r.status_code != 200:
        print r.text
        exit()
    for m in json.loads(r.text)['messages']:
        if m['type'] == 'ROOM_JOIN' and m['channelId'] == ASR_CHANNEL:
            for user in m['users']:
                if 'p' in user['flags']:
                    continue
                if user['name'] in ASR:
                    present[ASR[user['name']]].append(user['name'])
            done = True
            break

now = datetime.utcnow().strftime('UTC %H:%M')

post_kgs({
    'type': 'CHAT',
    'channelId': ASR_CHANNEL,
    'text': "Howdy, I am ASRbot, a quick hack which will tell you who is currently available for playing ({}).".format(now)}, cookies=cookies)

for room in 'ALPHA', 'BETA', 'GAMMA', 'DELTA', 'PLACEMENT':
    post_kgs({
        'type': 'CHAT',
        'channelId': ASR_CHANNEL,
        'text': "{}: {}".format(room, ', '.join(present[room]) or 'Nobody! Sigh.')}, 
             cookies=cookies)

post_kgs({
    'type': 'CHAT',
    'channelId': ASR_CHANNEL,
    'text': "Have fun! Post suggestions for ASRbot in https://github.com/domeav/ASRbot/issues"}, cookies=cookies)


post_kgs({"type": "LOGOUT"}, cookies=cookies)
