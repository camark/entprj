# -*- coding: cp936 -*-

import wsgiref.handlers
import sys
import os



sys.path.append('modules')
sys.path.append('models')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from helloblog import *
from blog import *
from category import *
from time import gmtime,strftime

class NewBlogHandler(HelloBlog):  
  def get(self):
    if self.check_login(users.create_login_url(self.request.uri)):
      self.response.headers['Content-type']='text/html'
      self.template_values={
        'Categories':Category.all().fetch(1000)
        }
      self.render('templates/admin/new_blog.html')
       

  def post(self):
    if self.check_login(users.create_login_url(self.request.uri)):
      _title=self.param('title')
      _content=db.Text(self.param('contents'))
      _category_id=self.param('category_id')
      _category=Category.get(_category_id)
      _blog=Blog(
        title=_title,
        content=_content,
        category=_category,
        author=users.get_current_user()
        )
      _blog.put()

      self.redirect('/')

class DeleteBlog(HelloBlog):
  def get(self):
    _blog_id = int(self.request.path[len('/admin/blog/delete/'):])

    _blog=Blog.get_by_id(_blog_id)

    if _blog:
      _blog.delete()
      self.redirect('/')
    else:
      self.write('No blog find')

    
class NewCategory(HelloBlog):
  def get(self):
    if self.check_admin(users.create_login_url(self.request.uri)):
      self.render('templates/admin/new_category.html',{})

  def post(self):
    if self.check_admin(users.create_login_url(self.request.uri)):
      cat_name=self.param('cat_name')

      category=Category(name=cat_name)

      category.put()
      if category.is_saved():
        self.redirect('/admin/category/list')
      else:
        self.write('Save Error!')
        
class ListCategory(HelloBlog):
  def get(self):
    cats=Category.all().fetch(50)
    self.template_values={
      'Categories':cats
      }
    self.render('templates/admin/list_category.html')

class DeleteCategory(HelloBlog):
  def get(self):
    url=self.request.path
    _blog_id=url[23:]

    self.write(_blog_id)
    
class BlogAdmin(HelloBlog):
    def get(self):
        if self.check_login(users.create_login_url(self.request.uri)):
            if not users.is_current_user_admin():
                self.write('You must be the Administator!')
            else:
                self.render('templates/admin_index.html',{})

class DeleteComment(HelloBlog):
  def get(self):
    _comment_id= int(self.request.path[len('/admin/comment/delete/'):])

    _comment=Comment.get_by_id(_comment_id)

    if _comment:
      _comment.delete()


class IntrepidSourceList(HelloBlog):
  def get(self):
    self.mirrors={
    'Archive.ubuntu.com���·�������ŷ�ޣ���Ϊ�ٷ�Դ��������ͨ�û�ʹ��)':'http://archive.ubuntu.com/ubuntu/',
    'Ubuntu.cn99.com���·�����������ʡ�����е��ţ��Ƽ������û�ʹ�ã�':'http://ubuntu.cn99.com/ubuntu/',
    'Mirrors.shlug.org���·����������ŷ�������Ubuntu China Official Mirror, maintained by Shanghai Linux User Group��':'http://cn.archive.ubuntu.com/ubuntu',
    'Mirror.lupaworld.com���·��������㽭ʡ������˫�߷�������':'http://mirror.lupaworld.com/ubuntu',
    '���Ŵ�ѧ���·���������������������':'ftp://ubuntu.realss.cn/ubuntu/',
    '�ɶ��� ���ӿƼ���ѧ���·����������������Ƽ�У԰������ͨ�û�ʹ�ã�':'http://ubuntu.uestc.edu.cn/ubuntu/',
    '�ɶ��� ���ӿƼ���ѧ���·�����2':'http://ubuntu.dormforce.net/ubuntu/',
    '�Ϻ����Ϻ���ͨ��ѧ���·����������������Ƽ�У԰������ͨ�û�ʹ�ã�':'http://ftp.sjtu.edu.cn/ubuntu/',
    '�й���ѧ������ѧ���·����������������Ƽ�У԰������ͨ�û�ʹ�ã�':'http://debian.ustc.edu.cn/ubuntu/',
    '�й�̨�� ̨���ѧ���·��������Ƽ���ͨ�û�ʹ�ã�����PINGƽ����Ӧ�ٶ�41MS��ǿ���Ƽ���Դ���Ƚ����������ٳ���ͬ�����⣩':'http://ubuntu.csie.ntu.edu.tw/ubuntu/',
    'mirror.rootguide.org���·��������Ϻ��� ���ţ�':'http://mirror.rootguide.org/ubuntu/',
    '̨��Ĺٷ�Դ�ٶ�Ҳ�൱������ʱ���������ڵص�':'http://tw.archive.ubuntu.com/ubuntu'
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

  self.template_values = {
    'SourceLists':self.mirrors,
    'IncludeSource':True,
    'Output':''
    }

  self.render('templates/IntrepidSource.html')

  def post(self):
    iSel =self.param('mirror_id')
    include_src = self.param('include_src')
    output = []

    url = self.mirros[self.mirrors[iSel])

    for deb_url in self.mirror_url:
      output.append( deb_url )

    if include_src:
      for deb_url in self.mirror_src_url:
        output.append( deb_url )

    result = ''
    for o in output:
      result = result+ os.linesep
      
    self.template_values = {
    'SourceLists':self.mirrors,
    'IncludeSource':True,
    'Output': result
    }
    
    

def main():
  application = webapp.WSGIApplication([
    ('/admin', BlogAdmin),
    ('/admin/blog/new',NewBlogHandler),
    ('/admin/blog/delete/.*',DeleteBlog),
    ('/admin/category/delete/.*',DeleteCategory),
    ('/admin/category/new',NewCategory),
    ('/admin/category/list',ListCategory)
    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
