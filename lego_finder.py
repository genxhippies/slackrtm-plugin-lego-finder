import re
import urllib2
import traceback
import datetime

import logging

crontable = []
outputs = []

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

    try:
        for num in re.findall(r'\d+', text):
            p_info = get_product_info(num)

            if p_info['found']:
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

