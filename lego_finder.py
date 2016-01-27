# -*- coding: utf-8 -*-

import re
import urllib2
import traceback
import datetime
import time

import logging

crontable = []
outputs = []

unit_string = [
    u'미터',
    u'밀리미터',
    u'센티미터',
    u'킬로미터',
    u'그램',
    u'킬로그램',
    u'시',
    u'분',
    u'초',
    u'개',
    u'일',
    u'월',
    u'년',
    'm',
    'mm',
    'cm',
    'km',
    'mi',
    'mile',
    'ft',
    'inch',
    'g',
    'kg',
    'ton[s]?',
    'hour[s]?',
    'min',
    'minute[s]?',
    'sec',
    'second[s]?',
    'year[s]?',
    'month[s]?',
    'day[s]?',
]

search_history = []
MAX_HISTORY_LENGTH = 5
HISTORY_LIVE_TIME = 60

ignore_patterns = [
    r'<[^<>]*>',        # tag
    r'[0-9]+:[0-9]+',   # time format
]

def get_product_info(pn):
    r = {}
    opener = urllib2.build_opener()
    url = 'https://alpha.bricklink.com/pages/clone/catalogitem.page?S={pn}'.format(pn = pn)
    r['url'] = url

    request = urllib2.Request(url)
    request.add_header('User-Agent', 'LegoBot/1.0 +http://iizs.slack.com/')
    body = opener.open(request).read()

    r['found'] = False
    if body.find('No Item(s) were found') == -1 :
        m_name = re.search("strItemName:\s+'([^']+)'", body)
        if m_name == None:
            r['found'] = False
        else:
            r['found'] = True
            r['title'] = m_name.group(1)
            m_image = re.search("_var_images.push\( { isBig: true, url: '([^']+)'", body)
            if m_image != None:
                r['image'] = "https:" + m_image.group(1)

    return r


def _process_text(text, channel):
    logging.info('[Process text] %s'%text)

    for igp in ignore_patterns:
        text = re.sub(igp, '[REPL]', text)

    for us in unit_string:
        text = re.sub('[0-9]+[ \t]*%s'%us, '[REPL]', text)

    while len(search_history)>0 and (time.time()-search_history[0]['time'])>HISTORY_LIVE_TIME:
        search_history.pop(0)

    search_history_map = {sh["code"]:True for sh in search_history}
    try:
        for num in re.findall(r'\d+', text):
            if search_history_map.get(num):
                outputs.append([channel, "{pn} : already searched".format(pn = num)])
                continue

            p_info = get_product_info(num)

            if p_info['found']:
                if len(search_history)>MAX_HISTORY_LENGTH:
                    outputs.append([channel, "I do not want to be a spambot"])
                    return

                search_history.append({
                    'code':num,
                    'time':time.time()
                })

                print "[" + str(datetime.datetime.now()) + "] " + num + ": " + p_info['title']
                outputs.append([channel, "{pn} : {name}".format(pn = num, name = p_info['title'])])
                outputs.append([channel, "{url}".format(url = p_info['url'])])
                if 'image' in p_info:
                    outputs.append([channel, "{image}".format(image = p_info['image'])])
    except Exception as e:
        print traceback.format_exc()
        raise e


def process_message(data):

    if 'text' in data:
        _process_text(data['text'], data['channel'])

