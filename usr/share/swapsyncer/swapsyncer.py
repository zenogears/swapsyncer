#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import requests
import json
import sys
import pythonzenity
import getpass
import time

from datetime import datetime
from decimal import Decimal

from pythonzenity import Question
from pythonzenity import Warning
from pythonzenity import GetDirectory
from pythonzenity import InfoMessage
from pythonzenity import TextInfo
from pythonzenity import Progress

## Debug
debug_ON = 1

def debug(anything):
    if debug_ON:
        print(anything)

##Site
url = "http://hacktech.xyz/swap/"

conf_dir_path = "/home/" + getpass.getuser() + "/.swapsyncer"
debug("Config directory path: {0}".format(conf_dir_path))

conf_path = conf_dir_path + "/config.ini"
log_path = conf_dir_path + "/swapsyncer.log"

debug("Config path: {0}\nLog Path: {1}".format(conf_path,log_path))

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))

now = datetime.now()
date = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
debug("Date: {0}".format(date))
out_string = ""

## Create conf dir if not exist
if not os.path.exists(conf_dir_path):
    debug("Create config directory")
    os.makedirs(conf_dir_path)

## create log and conf files if not exist  
lp = open(log_path, 'a+')
fp = open(conf_path, 'a+')

## create conf. file
if os.stat(conf_path).st_size == 0:
    if (Question(text="Конфиг не найден.\nДиректория SWAP не определена.\nХотите указать директорию под SWAP?")):
        swapdir = GetDirectory(sep=None)
        fp.write(str(swapdir)[2:-2])
        fp.close()

#if not lp.read():
#  lp.write(str(date))
#  lp.close()

fp = open(conf_path)
lp = open(log_path, 'w+')

eboots_path = str(fp.read())
fp.close()
   
if not os.path.exists(eboots_path):
    debug("Something gone wrong")
    Warning("Директория SWAP не найдена")

else:
    local_eboots = ([ f for f in os.listdir(eboots_path) if f.endswith('.bin') and os.path.isfile(os.path.join(eboots_path,f)) ])
    r = requests.get(url  + '/list.php')
    remote_eboots = r.json()
    download_list = list(set(remote_eboots) - set(local_eboots))
    upload_list = list(set(local_eboots) - set(remote_eboots))

    if len(download_list) == 0:
            out_string += "Нечего скачивать.\n"
    else:
        lp.write(str(date) + "\n")
        InfoMessage(text=str(len(download_list)) + " файлов будет скачано")
        testparam = float(100/float(len(download_list)))
        update = Progress(text='Downloading...', percentage=0, width=470, auto_close=True)
    i = 1;
    palka = 0;

    for fn in download_list:
        lp.write("D[ {0} / {1} ] {2}".format(i,len(download_list),fn))
        debug("Download: [ {0} / {1} ] {2}".format(i,len(download_list),fn))
        i+=1
        palka = round(float(palka) + float(testparam),2)
        files_to_download = len(download_list) - i
        datchik = int(palka)
        update(datchik,'Download: {0} % \tFiles: {1}'.format(palka,files_to_download))
        r = requests.get(url + "/SWAP/" + fn)
        with open(eboots_path + '/' + fn, 'wb') as fd:
            fd.write(r.content)
            fd.close()

    if len(upload_list) == 0:
        out_string += "Нечего закачивать.\n"
    else:
        InfoMessage(text=str(len(upload_list)) + " файлов будет загружено")
        testparam = float(100/float(len(upload_list)))
        update = Progress(text='Uploading...', percentage=0, width=470, auto_close=True)
        lp.write(str(date) + "\n")

    i = 1;
    palka = 0;

    for fn in upload_list:
        lp.write ("U[" + str(i) + "/" + str(len(upload_list)) + "]" + fn + "\n")
        i+=1
        palka = float(palka) + float(testparam)
        datchik = int(palka)
        update(datchik,"Загружаем данные на сервер, подождите... Это может занять длительное время. Загружено: " + str("%.1f" % palka) + " %")
        r = requests.post(url + "/uploadify.php", files={'Filedata': open(eboots_path + '/' + fn, 'rb')})
    lp.close();

    if len(out_string) > 0:
        InfoMessage(text=out_string)
    if len(upload_list)>0 or len(download_list)>0:
      if (Question(text="Желаете посмотреть изменения?")):
        TextInfo(filename=log_path, editable=False, width=400, height=200)
