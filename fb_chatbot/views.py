    #!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, requests, random, re
from pprint import pprint

from django.shortcuts import render
from django.http import HttpResponse

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from fuzzywuzzy import process

# Create your views here.

PAGE_ACCESS_TOKEN = 'EAAZAg3eueoxUBAAdTsps670ekn6haHMS7kH0RVZBCsztWhkjuZBYJ60jQ318lv0PAXJHagBN6CHrhOWWf3pMHrC6p7LI7jnHAIAVY6P26BfX5d6JIp5oZC7tAmJLBnP9bQ6DxnujWu0Gr15Xvnq8vFT2mZBmgJwaHJRleH6nNWQZDZD'
VERIFY_TOKEN = '8447789934m'

def logg(mess,meta='log',symbol='#'):
  print '%s\n%s\n%s'%(symbol*20,mess,symbol*20)

def index(request):
    #set_greeting_text()
    handle_postback('asdasd','asd')
    #whitelist_domain()
    set_persistent_menu()
    post_facebook_message('100006427286608','mango')
    output_content = faq_search()
    #scrape_spreadsheet()

    output_content = get_offer_object('fbid')
    logg(output_content,symbol='^**^')
    output_content = scrape_spreadsheet(sheet_type='newsletter1')
    return HttpResponse(output_content, content_type='application/json')

def get_newsletter_object(fbid):
    spread_arr = scrape_spreadsheet()
    item_arr =[]
    for i in spread_arr:
        d = {}
        #underscrores will get removed from key names
        d['title'] = i['title']
        d['item_url'] = 'https://paytm.com'
        d['image_url'] = i['images']
        d['subtitle'] = i['description']
        d['buttons'] = []
        d['buttons'].append( dict(type='web_url',url="https://paytm.com",title='Claim Offer') )
        item_arr.append(d)

    output_content = gen_array_response(fbid,item_arr)
    return json.dumps(output_content)


def get_offer_object(fbid):
    spread_arr = scrape_spreadsheet()
    item_arr =[]
    for i in spread_arr:
        d = {}
        #underscrores will get removed from key names
        d['title'] = i['itemname']
        d['item_url'] = i['itemlink']
        d['image_url'] = i['itempicture']
        d['subtitle'] = i['itemdescription']
        d['buttons'] = []
        d['buttons'].append( dict(type='web_url',url=i['itemlink'],title='Claim Offer') )
        item_arr.append(d)

    output_content = gen_array_response(fbid,item_arr)
    return json.dumps(output_content)

def scrape_spreadsheet(sheet_type='offers'):
    offer_sheet_id = '1US5eDiy_oJkPyyvOFR8RKZCmaq2PMkPF7vgcEWloq3Y'
    event_sheet_id = '1Pp67pJId2WZzBXOx8qWT9fwW0F0rpx7R48gEzxp6pmI'
    newsletter_sheet_id = '1L9bfH89agYGdkBA0EQmM5e4phiOoHJTVfw4TZSa74e8'

    if sheet_type == 'offers':
        sheet_id = offer_sheet_id
    else:
        sheet_id = newsletter_sheet_id

    url = 'https://spreadsheets.google.com/feeds/list/%s/od6/public/values?alt=json'%(sheet_id)

    resp = requests.get(url=url)
    data = json.loads(resp.text)
    arr =[]
    for entry in data['feed']['entry']:
        d = {}
        for k,v in entry.iteritems():
            if k.startswith('gsx'):
                key_name = k.split('$')[-1]
                d[key_name] = entry[k]['$t']
        #print d
        arr.append(d)
    print arr    
    return arr

def set_greeting_text():
    post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%PAGE_ACCESS_TOKEN
    greeting_text = "Hello and welcome to my bot"
    greeting_object = json.dumps({"setting_type":"greeting", "greeting":{"text":greeting_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=greeting_object)
    pprint(status.json())

def set_persistent_menu():
    post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%PAGE_ACCESS_TOKEN
    
    menu_object = {
            "setting_type" : "call_to_actions",
            "thread_state" : "existing_thread",
            "call_to_actions":[
                {
                    "type":"postback",
                    "title":"PayTM Login",
                    "payload":"HELP"
                },
                {
                    "type":"postback",
                    "title":"Call a human",
                    "payload":"CALL_US"
                },
                {
                    "type":"postback",
                    "title":"Offers & Coupons",
                    "payload":"OFFERS"
                },
                {
                    "type":"postback",
                    "title":"News",
                    "payload":"NEWS"
                },
                {
                    "type":"postback",
                    "title":"Download App",
                    "payload":"DOWNLOAD"
                }
            ]
    }
    menu_object = json.dumps(menu_object)
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=menu_object)
    logg(status.json(),symbol='---**---')
    pprint(status.json())

def whitelist_domain(domain='https://github.com'):
    post_message_url = "https://graph.facebook.com/v2.6/me/thread_settings?access_token=%s"%PAGE_ACCESS_TOKEN
    
    whitelist_object = {
      "setting_type" : "domain_whitelisting",
      "whitelisted_domains" : [domain],
      "domain_action_type": "add"
    }
    whitelist_object = json.dumps(whitelist_object)
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=whitelist_object)
    logg(status.json(),symbol='---WW---')
    pprint(status.json())


def faq_search(search_string ='order'):
    with open('faq.json') as data_file:    
        data = json.load(data_file)

    for k,v in data['one_word_query'][0].iteritems():
        if search_string in k.lower():
            return v

    arr = []
    for k,v in data['FAQ'].iteritems():
        for i in v:
            for k1,v1 in i.iteritems():
                arr.append(v1)

    result_arr = process.extract(search_string, arr, limit=2)
    result_arr = [i[0].split(':')[-1] for i in result_arr]
    return result_arr[0]

def gen_array_response(fbid,item_arr):
    if not item_arr:
        item_arr = []

    elements_arr = []
    for i in item_arr:
        button_arr = []
        for button in i['buttons']:
            button_item = {
                            "type":button['type'],
                            "url":button['url'],
                            "title":button['title']
                          }
            button_arr.append(button_item)

        share_button = {"type":"element_share"} 
        button_arr.append(share_button)

        sub_item = {
                        "title":i['title'],
                        "item_url":i['item_url'],
                        "image_url":i['image_url'],
                        "subtitle":i['subtitle'],
                        "buttons":button_arr
                    }

        elements_arr.append(sub_item)

    response_msg_generic = {

            "recipient":{
                "id":fbid
              },
              "message":{
                "attachment":{
                  "type":"template",
                  "payload":{
                    "template_type":"generic",
                    "elements":elements_arr
                  }
                }
              }
    }

    return response_msg_generic


def post_facebook_message(fbid, recevied_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    recevied_message = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower()
    
    if len(recevied_message) < 4:
        response_text = 'Could not understand that :('
    else:        
        response_text = faq_search(search_string=recevied_message)

    if type(response_text) == dict:
        response_msg = {

                "recipient":{
                    "id":fbid
                  },
                  "message":{
                    "attachment":{
                      "type":"template",
                      "payload":{
                        "template_type":"generic",
                        "elements":[
                          {
                            "title":response_text['title'],
                            "item_url":response_text['link'],
                            "image_url":response_text['images'],
                            "subtitle":response_text['description'],
                            "buttons":[
                              {
                                "type":"web_url",
                                "url":response_text['link'],
                                "title":"Go to paytm"
                              },  
                              {
                                "type":"element_share"
                              }         
                            ]
                          }
                        ]
                      }
                    }
                  }

        }
        response_msg = json.dumps(response_msg)

    else:
        response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":response_text}})

    if recevied_message in 'offers,offer,cashback,coupons'.split(','):
        response_msg = get_offer_object(fbid)

    if recevied_message in 'news,newsletter'.split(','):
        response_msg = get_newsletter_object(fbid)

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)


def handle_postback(fbid,payload):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    
    logg(payload,symbol='*')
    response_text = ''
    response_object = ''
    
    if payload == 'HELP':
        response_text = 'HELP'
    elif payload == 'CALL_US':
         
        response_object={
                          "recipient":{
                            "id":fbid
                          },
                          "message":{
                            "attachment":{
                              "type":"template",
                              "payload":{
                                "template_type":"button",
                                "text":"Need further assistance ? Speak to us on our toll free number.",
                                "buttons":[
                                  {
                                            "type":"phone_number",
                                            "title":"Call Us",
                                            "payload":"+911203062244"
                                  }
                                ]
                              }
                            }
                          }
                        }
    elif payload == 'OFFERS':
        post_facebook_message(fbid,'offers')

    elif payload == 'DOWNLOAD':
        response_object = {

                "recipient":{
                    "id":fbid
                  },
                  "message":{
                    "attachment":{
                      "type":"template",
                      "payload":{
                        "template_type":"generic",
                        "elements":[
                          {
                            "title":'Download PayTM app',
                            "image_url":'https://lh5.ggpht.com/QODLrHuQBnWmDSVd4hSVWCFyCaiyilExf6nvdEKuugcCLh9tNOl7uVxTFffVKrHatpHs=w300-rw',
                            "subtitle":"#PaytmKaro for the fastest online recharge, bill & utility payment and online shopping experience. Quick, easy and secure",
                            "buttons":[
                              {
                                "type":"web_url",
                                "url":'https://play.google.com/store/apps/details?id=net.one97.paytm&hl=en',
                                "title":"Android"
                              },
                              {
                                "type":"web_url",
                                "url":'https://itunes.apple.com/us/app/recharge-bill-payment-wallet/id473941634?mt=8',
                                "title":"iPhone"
                              }         
                            ]
                          },
                          {
                            "title":'PayTM Seller app',
                            "image_url":'https://lh3.googleusercontent.com/9H7pVuBIaiGkqlq2-e41qPOUy-74AsYIiBSOHmZFLI9dzQ5PFQPRx9y0KM70hp6v5g=w300-rw',
                            "subtitle":"Paytm Seller app lets you become a seller in few easy steps, manage product listings and process orders on the go",
                            "buttons":[
                              {
                                "type":"web_url",
                                "url":'https://play.google.com/store/apps/details?id=com.paytm.merchants&hl=en',
                                "title":"Android"
                              },
                              {
                                "type":"web_url",
                                "url":'https://itunes.apple.com/in/app/paytm-seller/id1142583481?mt=8',
                                "title":"iPhone"
                              }         
                            ]
                          }
                        ]
                      }
                    }
                  }

        }


    if response_text:
        response_object = json.dumps({"recipient":{"id":fbid}, "message":{"text":response_text}})
    else:
        response_object = json.dumps(response_object)

    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_object)
    logg(status.json(),symbol='---297---')
    return


class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        incoming_message= json.loads(self.request.body.decode('utf-8'))
        
        logg(incoming_message)

        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                try:
                    if 'postback' in message:
                        handle_postback(message['sender']['id'],message['postback']['payload'])
                        return HttpResponse()
                    else:
                        pass
                except Exception as e:
                    logg(e,symbol='-315-')

                try:
                    sender_id = message['sender']['id']
                    message_text = message['message']['text']
                    post_facebook_message(sender_id,message_text) 
                except Exception as e:
                    logg(e,symbol='-332-')

        return HttpResponse()  



