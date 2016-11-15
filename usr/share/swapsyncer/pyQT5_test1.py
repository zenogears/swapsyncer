#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import requests
import json
import sys
import pythonzenity
import getpass
import time

from datetime import datetime
from decimal import Decimal
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QWidget,
    QAction, QFileDialog, QApplication, QProgressBar, QPushButton, qApp, QHBoxLayout, QFrame, QSplitter, QLabel)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtCore import Qt

debug_ON = True

def debug(anything):
    if debug_ON:
        print(anything)

##Site
url = "http://swapbase.ru/"

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
mycind = True

## Create conf dir if not exist
if not os.path.exists(conf_dir_path):
    debug("Create config directory")
    os.makedirs(conf_dir_path)

## create log and conf files if not exist  
lp = open(log_path, 'a+')
fp = open(conf_path, 'a+')

## create conf. file
if os.stat(conf_path).st_size == 0:
    mycind = False

#if not lp.read():
#  lp.write(str(date))
#  lp.close()

fp = open(conf_path)
lp = open(log_path, 'w+')

eboots_path = str(fp.read())
fp.close()

class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):

        if not os.path.exists(eboots_path):
            debug("Something gone wrong")
            self.showDialog()

        else:
            self.local_eboots = ([ f for f in os.listdir(eboots_path) if f.endswith('.bin') and os.path.isfile(os.path.join(eboots_path,f)) ])
            r = requests.get(url  + '/list.php')
            self.remote_eboots = r.json()
            self.download_list = list(set(self.remote_eboots) - set(self.local_eboots))
            self.upload_list = list(set(self.local_eboots) - set(self.remote_eboots))
            #debug("{0}".format(len(self.download_list),self.download_list))

        openDir = QAction(QIcon('/mnt/Video/debianpack/swapsyncer/usr/share/icons/hicolor/24x24/apps/openx24.png'), 'Open SWAP directory', self)
        openDir.setShortcut('Ctrl+O')
        openDir.setStatusTip('Open SWAP directory')
        openDir.triggered.connect(self.showDialog)

        exitAction = QAction(QIcon('/mnt/Video/debianpack/swapsyncer/usr/share/icons/hicolor/24x24/apps/exitx24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit')
        exitAction.triggered.connect(qApp.quit)

        self.toolbar = self.addToolBar('Open')
        self.toolbar.addAction(openDir)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 300, 25)

        if len(self.download_list) > 0:
            self.btn1 = QPushButton('Download: {0:6} files'.format(len(self.download_list)), self)
        else:
            self.btn1 = QPushButton('Nothing to download', self)
            self.pbar.setValue(100)

        self.btn1.move(100, 80)
        self.btn1.resize(150, 30)
        self.btn1.clicked.connect(self.doActionDownload)

        self.step1 = 0

        self.ubar = QProgressBar(self)
        self.ubar.setGeometry(30, 120, 300, 25)

        if len(self.upload_list) > 0:
            self.btn2 = QPushButton('Upload: {0:6} files'.format(len(self.upload_list)), self)
        else:
            self.btn2 = QPushButton('Nothing to upload', self)
            self.ubar.setValue(100)

        self.step2 = 0

        
        self.btn2.move(100, 160)
        self.btn2.resize(150, 30)
        self.btn2.clicked.connect(self.doActionUpload)
        

        self.lbl1 = QLabel('SWAP directory:', self)
        self.lbl1.move(10, 190)
        self.lbl1.resize(400, 15)
        if eboots_path:
            self.lbl2 = QLabel(eboots_path, self)
            self.lbl2.resize(400, 15)
            #debug(eboots_path)
            self.lbl2.move(10, 210)
        else:
            self.lbl1 = QLabel('Please, add SWAP directory', self)
            self.lbl1.move(10, 190)
            self.lbl1.resize(400, 15)

        self.setGeometry(300, 300, 350, 240)
        self.setWindowTitle('ToolBar')
        self.show()


    def showDialog(self):

        self.eboots_path = QFileDialog.getExistingDirectory(self, 'Open directory', '/home')
        if self.eboots_path:
            with open(conf_path, 'w') as fp:
                fp.write(str(self.eboots_path))
                #debug(self.eboots_path)
            sys.exit()

    def doActionDownload(self):
        if self.download_list is not None and len(self.download_list) > 0:
            self.i = 1;
            self.palka = 0;

            for fn in self.download_list:
                lp.write("D[ {0} / {1} ] {2}".format(self.i,len(self.download_list),fn))
                debug("Download: [ {0} / {1} ] {2}".format(self.i,len(self.download_list),fn))
                self.i+=1
                self.palka = round(float(self.palka) + float(100/float(len(self.download_list))),4)
                self.files_to_download = len(self.download_list) + 1 - self.i
                self.btn1.setText('Downloading: {0:6}'.format(self.files_to_download))

                if self.files_to_download > 0:
                    self.pbar.setValue(self.palka)
                    #debug(self.palka)
                else:
                    self.pbar.setValue(100)
                    self.btn1.setText('Nothing to download')

                r = requests.get(url + "/SWAP/" + fn)
                with open(eboots_path + '/' + fn, 'wb') as fd:
                    fd.write(r.content)
                    fd.close()

            self.download_list = None

        else:
            self.pbar.setValue(100)
            self.btn1.setText('Nothing to download')


    def doActionUpload(self):

        if self.upload_list is not None and len(self.upload_list) > 0:
            self.i = 1;
            self.palka = 0;

            for fn in self.upload_list:
                lp.write("U[ {0} / {1} ] {2}".format(self.i,len(self.upload_list),fn))
                debug("Upload: [ {0} / {1} ] {2}".format(self.i,len(self.upload_list),fn))
                self.i+=1
                self.palka = round(float(self.palka) + float(100/float(len(self.upload_list))),4)
                self.files_to_upload = len(self.upload_list) + 1 - self.i
                self.btn2.setText('Uploading: {0:6}'.format(self.files_to_upload))

                if self.files_to_upload > 0:
                    self.ubar.setValue(self.palka)
                    #debug(self.palka)
                else:
                    self.ubar.setValue(100)
                    self.btn2.setText('Nothing to upload')

                r = requests.post(url + "/uploadify.php", files={'Filedata': open(eboots_path + '/' + fn, 'rb')})

            self.upload_list = None

        else:
            self.ubar.setValue(100)
            self.btn2.setText('Nothing to upload')

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())