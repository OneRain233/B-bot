#!/usr/bin/env python3

from distutils.command.config import config
from shutil import ExecError
from time import sleep
from typing import *
import os
from pathlib import Path
# from mongoDatabase import *
failed = {}

resource_dir = str(Path())

def send_failed_mail(messages: Dict[str, str], address):
    import smtplib
    from email.mime.text import MIMEText
    config = readConfig('config.yaml')
    host = config['email']['host']
    user = config['email']['user']
    password = config['email']['password']
    sender = config['email']['sender']
    receivers = address

    content = ''
    for m in messages:
        content += m
        content += ": "
        content += messages[m]
        content += "\n\n"

    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = '体温自动填报失败'
    message['From'] = sender
    message['To'] = receivers[0]

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(host, 25)
        smtpObj.login(user, password)
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        smtpObj.quit()
    except smtplib.SMTPException as e:
        print('send mail failed', e)


def report(studentId: str, password: str, temp: str,
           faProvince: str, faCity: str, faCounty: str,
           faProvinceName: str, faCityName: str, faCountyName: str, address) -> bool:
    import requests
    from subprocess import Popen, PIPE
    from bs4 import BeautifulSoup

    def selectInput(soup: BeautifulSoup, attrs: Dict[str, str]) -> str:
        return soup.find('input', attrs=attrs).attrs['value']

    def selectInputByName(soup: BeautifulSoup, name: str) -> str:
        return selectInput(soup, attrs={'name': name})

    def selectInputById(soup: BeautifulSoup, id: str) -> str:
        return selectInput(soup, attrs={'id': id})

    sess = requests.Session()

    r = sess.get(
        "https://cas.swjtu.edu.cn/authserver/login?service=http://xgsys.swjtu.edu.cn/cas/onelogin.aspx?type=SPCP")
    soup = BeautifulSoup(r.text, 'html.parser')
    salt = selectInputById(soup, 'pwdDefaultEncryptSalt')
    lt = selectInputByName(soup, 'lt')
    dllt = selectInputByName(soup, 'dllt')
    exec = selectInputByName(soup, 'execution')

    # I just copied encrypt part of login from Chrome dev console
    js_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'encrypt.js')
    process = Popen(["node", str(js_file), password, salt], stdout=PIPE)
    
    (output, _) = process.communicate()
    process.wait()
    password = output.decode("utf-8").replace('\n', '')

    r = sess.post("https://cas.swjtu.edu.cn/authserver/login", data={
        'username': studentId,
        'passwordEncrypt': password,
        'password': password,
        'lt': lt,
        'dllt': dllt,
        'execution': exec,
        '_eventId': 'submit',
        'rmShown': 1
    })

    if r.text.find('<script>\'' + studentId + '\'</script>') == -1:
        print('登陆失败')
        return False

    print(studentId + ': 登陆成功')
    redirect_url = ''
    for line in r.text.splitlines():
        if line.find('http://xgsys.swjtu.edu.cn/SPCPTest3/Web/Account/CasLoginCallBack?par=') != -1:
            line = line.replace('window.location.href = ', '')
            line = line.replace(';', '')
            line = line.replace('\'', '')
            line = line.strip()
            redirect_url = line
            print(studentId + ': 重定向到填报首页: ' + redirect_url)

    r = sess.get(redirect_url)

    print(studentId + ': 开始填报 ')
    r = sess.get('http://xgsys.swjtu.edu.cn/SPCPTest3/Web/Report/Index')
    if r.text.find('每次填报间隔时间应不能小于4小时') != -1 or r.text.find('今天填报次数已完成，勿需再次填报!') != -1 or r.text.find(
            '当前采集日期已登记') != -1:
        print(studentId + ': 已填报')
        # send_failed_mail({studentId : ' 已填报'}, address)
        return '已填报'

    soup = BeautifulSoup(r.text, 'html.parser')

    data = {
        'StudentId': selectInputByName(soup, 'StudentId'),
        'IdCard': selectInputByName(soup, 'IdCard'),
        'Name': selectInputByName(soup, 'Name'),
        'Sex': selectInputByName(soup, 'Sex'),
        'SpeType': selectInputByName(soup, 'SpeType'),
        'CollegeNo': selectInputByName(soup, 'CollegeNo'),
        'SpeGrade': selectInputByName(soup, 'SpeGrade'),
        'SpecialtyName': selectInputByName(soup, 'SpecialtyName'),
        'ClassName': selectInputByName(soup, 'ClassName'),
        'MoveTel': selectInputByName(soup, 'MoveTel'),
        'Province': faProvince,
        'City': faCity,
        'County': faCounty,
        'ComeWhere': selectInputByName(soup, 'ComeWhere'),
        'ProvinceName': faProvinceName,
        'CityName': faCityName,
        'CountyName': faCountyName,
        'FaProvince': faProvince,
        'FaCity': faCity,
        'FaCounty': faCounty,
        'FaComeWhere': selectInputByName(soup, 'FaComeWhere'),
        'FaProvinceName': faProvinceName,
        'FaCityName': faCityName,
        'FaCountyName': faCountyName,
        'CurAreaName': faProvinceName+faCityName+faCountyName,
        'CurAreaCode': faCounty,
        'GetAreaUrl': '/SPCPTest3/Web/Report/GetArea',
        'radioCount': 4,
        'checkboxCount': 0,
        'blackCount': 0,
        'radio_1': soup.find('input', attrs={'name': 'radio_1', 'checked': 'checked'}).attrs['value'],
        'radio_2': soup.find('input', attrs={'name': 'radio_2', 'checked': 'checked'}).attrs['value'],
        'radio_3': soup.find('input', attrs={'name': 'radio_3', 'checked': 'checked'}).attrs['value'],
        'radio_4': soup.find('input', attrs={'name': 'radio_4', 'checked': 'checked'}).attrs['value'],
        'PZData': '[{"OptionName":"否，未感染","SelectId":"99243c67-bc34-435f-9d5a-d7fad7f3d39a","TitleId":"12b4a828-2ed3-4559-99f3-d84e8cab2810","OptionType":"0"},{"OptionName":"否，没有身处高中风险地区","SelectId":"a03d84a1-c24f-438d-8be6-ff4e8c14cb59","TitleId":"15e1bb64-bd72-4ea3-a8f9-e79c226a3ec3","OptionType":"0"},{"OptionName":"否，无接触","SelectId":"24ee3594-2612-4ef4-94ad-5c9f7d5deaed","TitleId":"c3cf045f-c257-4bce-8dd6-136d2d9f9694","OptionType":"0"},{"OptionName":"无以上状况","SelectId":"28c7ee37-8d47-47ac-aed6-d65f7467c90d","TitleId":"9cb1a236-0a22-4744-9d1d-841dc0679771","OptionType":"0"}]',
        'Other': '',
        'ReSubmiteFlag': soup.find('input', attrs={'name': 'ReSubmiteFlag'}).attrs['value'],
    }

    r = sess.post('http://xgsys.swjtu.edu.cn/SPCPTest3/Web/Report/Index', data=data)

    if r.text.find('提交成功') != -1:
        print(studentId + ': 填报成功')
        return '填报成功'
    else:
        print(studentId + ': 填报失败')
        # send_failed_mail({studentId : ' 填报失败'}, address)
        return '填报失败'


def getTime():
    import datetime as dt
    t = dt.datetime.utcnow()
    t = t + dt.timedelta(hours=8)
    return t


def getTemperature() -> int:
    import random
    return random.randint(4, 7)


def runCatching(studentId: str, fn: Callable[[], bool]):
    try:
        if not fn():
            print('Unknown Error occurred')
            failed[studentId] = 'Unknown Error occurred'
    except AttributeError as err:
        print(f'Unknown Error occurred: {err}')
        failed[studentId] = f'{err}'


def readConfig(name: str) -> dict:
    import os
    import yaml
    dirName = os.path.split(os.path.realpath(__file__))[0]
    yamlPath = os.path.join(dirName, name)
    return yaml.load(open(yamlPath, 'r', encoding='utf-8'), Loader=yaml.FullLoader)


def report_temp():
    print('\n\n' + str(getTime()))
    print('===========================================================')
    qaq = []
    # config_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.yaml')
    config_file = os.path.join(resource_dir, 'temp_config.yaml')
    try:
        students = readConfig(config_file)['students']
    except Exception as e:
        return str(e)
    # URI = "mongodb://172.26.0.3:27017"
    # db = Database(URI, 'users', 'user')
    # students = list(db.collection.find())
    # print(students)
    for s in students:
        # print(s['username'])
        # return
        temperature = "36." + str(getTemperature())
        try:
            statues=report(str(s['studentId']), str(s['password']), temperature,
                                                                str(s['faProvince']), str(s['faCity']), str(s['faCounty']),
                                                            str(s['faProvinceName']), str(s['faCityName']),
                                                            str(s['faCountyName']), str(s['email']))
        except Exception as e:
            qaq.append(str(s['studentId'])+" "+str(e))

        qaq.append(str(s['studentId'])+" "+str(statues))
    # send_failed_mail({'Status': "\n" + str("\n".join(qaq))}, '76054204@qq.com')
    return "\n".join(qaq)

if __name__ == "__main__":
    report_temp()