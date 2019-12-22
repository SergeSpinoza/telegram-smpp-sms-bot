# -*- coding: utf-8 -*-

import re
import logging
import sys
import yaml

sys.path.insert(1, './lib')
import smpplib
from urllib3.contrib.socks import SOCKSProxyManager

with open("settings.yaml", 'r') as ymlfile:
   cfg = yaml.safe_load(ymlfile)

# if you want to know what's happening
logging.basicConfig(level=cfg['log_level'])

# Bot var
bot_token = cfg['telegram']['bot_token']
channel_id = cfg['telegram']['channel_id']
# urllib3.contrib.pyopenssl.inject_into_urllib3()
proxy = SOCKSProxyManager(cfg['telegram']['proxy_host'], username=cfg['telegram']['proxy_login'], password=cfg['telegram']['proxy_pass'])


# Two parts, UCS2, SMS with UDH
# parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(u'Привет мир!\n' * 10)

client = smpplib.client.Client(cfg['smpp_goip']['host'], cfg['smpp_goip']['port'])
sms_destination_num = cfg['smpp_goip']['sim_num']

def getPdu(pdu):
   pdu.short_message
   russian_symbols_count = len(re.findall('[а-яё]', pdu.short_message.decode('utf-16be', errors='ignore'), re.I))
   if russian_symbols_count > 0:
      # print(pdu.short_message.decode('utf-16be', errors='ignore'))
      sms = pdu.short_message.decode('utf-16be', errors='ignore')
      source_addr = pdu.source_addr.decode()
      msg = "SMS to (%s) from (%s): %s" % (sms_destination_num, source_addr, sms)
      proxy.request('POST', "https://api.telegram.org/bot" + bot_token + "/sendMessage",
                    fields={"chat_id": channel_id, "text": msg, "disable_web_page_preview": "true"}).read()
   else:
      # print(pdu.short_message.decode())
      sms = pdu.short_message.decode()
      source_addr = pdu.source_addr.decode()
      msg = "SMS to (%s) from (%s): %s" % (sms_destination_num, source_addr, sms)
      proxy.request('POST', "https://api.telegram.org/bot" + bot_token + "/sendMessage",
                    fields={"chat_id": channel_id, "text": msg, "disable_web_page_preview": "true"}).read()

client.set_message_received_handler(getPdu)

client.connect()
client.bind_transceiver(system_id=cfg['smpp_goip']['system_id'], password=cfg['smpp_goip']['password'])

# Enters a loop, waiting for incoming PDUs
client.listen()

