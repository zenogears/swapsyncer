#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import requests
import json
import sys
import pythonzenity
import getpass

from datetime import datetime

from pythonzenity import Question
from pythonzenity import Warning
from pythonzenity import GetDirectory
from pythonzenity import InfoMessage
from pythonzenity import Progress

url = "http://swapbase.ru/"
username = getpass.getuser()
conf_dir_path = "/home/" + username + "/.swapsyncer"
conf_path = conf_dir_path + "/config.ini"
log_path = conf_dir_path + "/swapsyncer.log"
dir_path = os.path.abspath(os.path.dirname(sys.argv[0])) 
eboots_path = dir_path + "/SWAP"
eboots_path = eboots_path.decode('cp1251')

now = datetime.now()
date = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")

if not  os.path.exists(conf_dir_path):
  os.makedirs(conf_dir_path)
  
lp = open(log_path, 'a+')

fp = open(conf_path, 'a+')

if not fp.read():
  if (Question(text="Директория SWAP не определена. Хотите найти её?")):
    swapdir = GetDirectory(sep=None)
    fp.write(str(swapdir)[2:-2])
    fp.close()


if not lp.read():
  lp.write(str(date))
  lp.close()



fp = open(conf_path)
lp = open(log_path, 'w+')
lp.write(str(date) + "\n")

eboots_path = str(fp.read())
   
if not os.path.exists(eboots_path):
	Warning("Директория SWAP не найдена")
	
else:
	local_eboots = ([ f for f in os.listdir(eboots_path) if f.endswith('.bin') and os.path.isfile(os.path.join(eboots_path,f)) ])
	r = requests.get(url  + '/list.php')
	remote_eboots = r.json()
	download_list = list(set(remote_eboots) - set(local_eboots))
	upload_list = list(set(local_eboots) - set(remote_eboots))
	
	if len(download_list)==0:
		InfoMessage(text="Нечего скачивать")
	else:
		f_to_download = str(len(download_list)) + " файлов скачано"
		InfoMessage(text=f_to_download)
	i = 1;
	
	for fn in download_list:
		lp.write("D[" + str(i) + "/" + str(len(download_list)) + "]" + fn + "\n")
		i+=1
		r = requests.get(url + "/SWAP/" + fn)
		with open(eboots_path + '/' + fn, 'wb') as fd:
			fd.write(r.content)
			fd.close()
	if len(download_list)!=0:
		InfoMessage(text=str(len(upload_list)) + " файлов скачано")
		
	if len(upload_list)==0:
		InfoMessage(text="Нечего загружать")
	else:
		InfoMessage(text=str(len(upload_list)) + " files to upload")
	i = 1;
	for fn in upload_list:
		lp.write ("U[" + str(i) + "/" + str(len(upload_list)) + "]" + fn + "\n")
		i+=1
		r = requests.post(url + "/uploadify.php", files={'Filedata': open(eboots_path + '/' + fn, 'rb')})
	if len(upload_list)!=0:
		InfoMessage(text=str(len(upload_list)) + " files uploaded")
