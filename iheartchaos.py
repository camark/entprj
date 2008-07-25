#!/usr/bin/python

import HTMLParser
from urllib import urlopen
import re
import os
import sys
from threading import Thread

class IChaosParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.urls=[]

    def handle_starttag(self,tag,attrs):
        if tag=='a':
            for name,value in attrs:
                if name=='href':
                    if self.isUrl(value):
                        if self.urls.count(value)==0 and value.find('#')==-1:
                            self.urls.append(value)
                            #print value

    def isUrl(self,str):
        regpat='http://www.iheartchaos.com/(\d{4})/(\d{2})/(\d{2})/(\w+)'
        regx=re.compile(regpat)

        re_result=regx.match(str)
        if re_result:
            return True
        else:
            return False

class PicParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.download=PicDownload()

    def handle_starttag(self,tag,attrs):
        if tag=='img':
            for name,value in attrs:
                if name=='src':
                    #print value
                    if self.isDownload(value):
                        self.download.Download(value)
                        #print value

    def isDownload(self,imgurl):
        regpat='http://www.iheartchaos.com/wp-content/uploads/(\d{4})/(\d{2})/(\w+-?)*.jpg'
        regx=re.compile(regpat)

        re_result=regx.match(imgurl)
        if re_result:
            return True
        else:
            return False


class PicDownload:
    def __init__(self):
        pass

    def Download(self,imgurl):
        fileSaveDir=self.getSaveDir()
        fileName=imgurl.split('/')[-1]

        if not os.path.exists(fileSaveDir+'/'+fileName):
            print "Retriving %s......" %(fileName)
            socket=urlopen(imgurl)
            os.chdir(fileSaveDir)

            f=open(fileName,'wb')
            f.write(socket.read())
            f.close()

    def getSaveDir(self):
        if sys.platform=='win32':
            def_save_path='c:/temp'            
        elif sys.platform=='linux2':
            def_save_path=os.environ['HOME']+'/temp'

        if not os.path.exists(def_save_path):
                os.mkdir(def_save_path)
        return def_save_path
            
            

class DownThread(Thread):
    def __init__(self,url):
        Thread.__init__(self)
        self.pp=PicParser()
        self.url=url

    def run(self):
        a=urlopen(self.url).read()
        self.pp.feed(a)
    
a=urlopen('http://www.iheartchaos.com/category/girls-of-ihc/').read()
print 'Waiting to Read'
#print a

ichaos=IChaosParser()
ichaos.feed(a)

#pp=PicParser()
for url in ichaos.urls:
    dt=DownThread(url)
    dt.start()
#print a
    #pp.feed(a)



