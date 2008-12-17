#!/usr/bin/env python #
# -*- coding: UTF-8 -*-

import wsgiref.handlers
import sys

sys.path.append('modules')
sys.path.append('models')

from helloblog import *

class IntrepidSourceList(HelloBlog):
  def initialize(self,request,response):
    HelloBlog.initialize(self,request,response)

    self.mirrors={
    'Archive.ubuntu.com更新服务器（欧洲，此为官方源，电信网通用户使用)':'http://archive.ubuntu.com/ubuntu/',
    'Ubuntu.cn99.com更新服务器（江苏省常州市电信，推荐电信用户使用）':'http://ubuntu.cn99.com/ubuntu/',
    'Mirrors.shlug.org更新服务器':'http://cn.archive.ubuntu.com/ubuntu',
    'Mirror.lupaworld.com更新服务器（浙江省杭州市双线服务器）':'http://mirror.lupaworld.com/ubuntu',
    '厦门大学更新服务器（教育网服务器）':'ftp://ubuntu.realss.cn/ubuntu/',
    '成都市 电子科技大学更新服务器（教育网，推荐校园网和网通用户使用）':'http://ubuntu.uestc.edu.cn/ubuntu/',
    '成都市 电子科技大学更新服务器2':'http://ubuntu.dormforce.net/ubuntu/',
    '上海市上海交通大学更新服务器（教育网，推荐校园网和网通用户使用）':'http://ftp.sjtu.edu.cn/ubuntu/',
    '中国科学技术大学更新服务器（教育网，推荐校园网和网通用户使用）':'http://debian.ustc.edu.cn/ubuntu/',
    '中国台湾 台湾大学更新服务器':'http://ubuntu.csie.ntu.edu.tw/ubuntu/',
    'mirror.rootguide.org更新服务器（上海市 电信）':'http://mirror.rootguide.org/ubuntu/',
    '台湾的官方源速度也相当不错，有时甚至快于内地的':'http://tw.archive.ubuntu.com/ubuntu'
    }

    self.mirror_url=[
    'deb %s intrepid main restricted universe multiverse',
    'deb %s intrepid-security main restricted universe multiverse',
    'deb %s intrepid-updates main restricted universe multiverse',
    'deb %s intrepid-backports main restricted universe multiverse',
    'deb %s intrepid-proposed main restricted universe multiverse',
    ]

    self.mirror_src_url = [
    'deb-src %s intrepid main restricted universe multiverse',
    'deb-src %s intrepid-security main restricted universe multiverse',
    'deb-src %s intrepid-updates main restricted universe multiverse',
    'deb-src %s intrepid-backports main restricted universe multiverse',
    'deb-src %s intrepid-proposed main restricted universe multiverse',
    ]
    
  def get(self):
    mirrors = []
    for key in self.mirrors.keys():
      mirrors.append(key)
      
    self.template_values = {
    'mirrors':mirrors,
    'IncludeSource':True,
    'Output':''
    }

    self.render('templates/IntrepidSource.html')

  def post(self):
    iSel = self.param('mirror_id')

    include_src = self.param('include_src')

    
    mirrors = []

    mirror = self.mirrors[iSel.encode('utf8')]

    output = []
    
    for deb_url in self.mirror_url:
      output.append( deb_url % (mirror))

    if include_src == 'True':
      for deb_url in self.mirror_src_url:
        output.append( deb_url % ( mirror ))

    result = '#Ubuntu APT Source for %s ' % ( iSel ) + '\n'
    result = result + '#Generate from http://superwar3fan.appsoot.com/Intrepid' + '\n'
    result = result + '#Author Mail: gm8pleasure@gmail.com' + '\n'
    result = result + '\n'

    for o in output:
      result = result+o+'\n'
      
    for key in self.mirrors.keys():
      mirrors.append(key)
      
    self.template_values = {
    'mirrors':mirrors,
    'IncludeSource':True,
    'Output': result
    }
    self.render('templates/IntrepidSource.html')

def main():
  application = webapp.WSGIApplication([
    ('/Intrepid', IntrepidSourceList),
    ('/Intrepid/SourceGen', IntrepidSourceList),    
    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
