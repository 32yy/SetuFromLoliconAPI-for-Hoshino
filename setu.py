import os
import random
import requests
import re
import time
import shutil

from nonebot.exceptions import CQHttpError

from hoshino import R, Service, priv
from hoshino.util import FreqLimiter, DailyNumberLimiter

_max = 10

EXCEED_NOTICE = f'色鬼！居然一天能冲{_max}次，请明早5点后再来！'
_nlmt = DailyNumberLimiter(_max)
_flmt = FreqLimiter(5)

sv = Service('setu', manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)
setu_folder = R.img('lolicon/').path

 # 这是屏蔽词，自行修改
blacklist_word = ['妊娠', '怀孕', '流产', '人兽', '伪娘', '扶他', 'futa', '扶她', '孕妇',]

def setu_gener():
    while True:
        filelist = os.listdir(setu_folder)
        random.shuffle(filelist)
        for filename in filelist:
            if os.path.isfile(os.path.join(setu_folder, filename)):
                yield R.img('lolicon/', filename)

setu_gener = setu_gener()

def get_setu():
    return setu_gener.__next__()

@sv.on_rex(r'重置setu')
async def chongzhi(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '你说重置就重置？那猫猫岂不是很没有面子', at_sender=True)
        return
    uid = int(ev.message.extract_plain_text().strip('重置setu'))
    print(uid)
    print(type(uid))
    _nlmt.reset(uid)
    await bot.send(ev, '已重置次数', at_sender=True)

@sv.on_rex(r'setu')
async def setu(bot, ev): 
    
    uid = ev['user_id'
    if not _nlmt.check(uid):
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.send(ev, EXCEED_NOTICE, at_sender=True)
            return
    if not _flmt.check(uid):
        await bot.send(ev, '您冲得太快了，请稍候再冲', at_sender=True)
        if random.random() < 0.3:
            if not priv.check_priv(ev, priv.SUPERUSER):
                await bot.send(ev, R.img('zhatang.jpg').cqcode)
        return
    _flmt.start_cd(uid)
    _nlmt.increase(uid)
    
    kwd = ev.message.extract_plain_text().strip('新setu')
    kwd = kwd.strip(' ')
    print(kwd)
    if kwd in blacklist_word:
        await bot.send(ev,'咱能看点正常的东西吗', at_sender=True)
        return
    data = {
        "apikey":'', 
        'r18':0,   
        'keyword':kwd,  
        'num':1,       
        'size1200':False
        }

    response = requests.get('https://api.lolicon.app/setu/v2',params=data)
    html = response.text

    str1 = 'origin'
    try:
        urls = html[html.index(str1)+11:]
    except:
        await bot.send(ev, '没查到你要的色图，你到底想看啥？', at_sender=True)
        return
    urls = re.sub(r'\\','',urls)
    url_list = re.sub("'",'',urls)
    url_list = url_list.replace('[','')
    url_list = url_list.replace(']','')
    url_list = url_list.replace('}','')
    url_list = url_list.replace('"','')
    url_list = url_list.strip(',').split(',')
    print(url_list)

    d = 'C:/res/img/lolicon/'
    for url in url_list:
        try:
            path = d + url.split('/')[-1]

            if not os.path.exists(d):
                os.mkdir(d)

            r = requests.get(url)

            r.raise_for_status()

            with open(path, 'wb') as f:

                f.write(r.content)
                f.close()
                
                pic = get_setu2()
                await bot.send(ev, pic.cqcode)
                    
                shutil.rmtree(r"C:/res/img/lolicon")
        except:

            await bot.send(ev, "发不出来呜呜")
