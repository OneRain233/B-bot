import requests
import json
import time
import datetime

url_ctf_list = 'https://api.ctfhub.com/User_API/Event/getUpcoming'
url_ctf_info = 'https://api.ctfhub.com/User_API/Event/getInfo'

def ctf_list():
    ctflist = []
    data = {
        'offset':0,
        'limit':20,
    }
    headers = {'Content-Type': 'application/json'}
    req = requests.post(url = url_ctf_list,headers = headers,data = json.dumps(data))
    # print(req.text)
    j = json.loads(req.text)
    for i in j['data']['items']:
        id = i['id']
        title = i['title']
        start_time = datetime.datetime.fromtimestamp(i['start_time'])
        end_time = datetime.datetime.fromtimestamp(i['end_time'])
        # print(str(id)+" "+str(title)+" "+str(start_time)+" "+str(end_time))
        ctflist.append(str(id)+" "+str(title)+" "+str(start_time)+" "+str(end_time))
        ctflist.append("-----------")
    return "\n".join(ctflist)

def ctf_info(a):
    data = {
        'event_id':a,
    }
    headers = {'Content-Type': 'application/json'}
    req = requests.post(url=url_ctf_info,headers = headers, data = json.dumps(data))
    # print(req.text)
    j = json.loads(req.text)
    raw = j['data']
    id = raw['id']
    details = raw['details']
    start_time = datetime.datetime.fromtimestamp(raw['start_time'])
    end_time = datetime.datetime.fromtimestamp(raw['end_time'])
    form = raw['form']
    official_url = raw['official_url']
    title = raw['title']
    return raw


