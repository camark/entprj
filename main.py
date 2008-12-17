#!/usr/bin/env python #
# -*- coding: UTF-8 -*-

import wsgiref.handlers
import sys
import urllib
import datetime
import os

sys.path.append('modules')
sys.path.append('models')

import PyRSS2Gen
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from helloblog import *
from blog import *
from category import *
from time import gmtime,strftime




class MainHandler(webapp.RequestHandler):
  
  def get(self):
    user=users.get_current_user()
  	
    if user:
      userName=user.nickname()
      now=strftime('%Y-%m-%d',gmtime())
      template_values={
        'userName':userName,
        'now':now
        }
      self.response.out.write(template.render('templates/hello.html',template_values))
    else:
      self.redirect(users.create_login_url(self.request.uri))



#Blog Show Function
class ListBlog(HelloBlog):
  def get(self):
    page=0
    show_prev_page = False
    show_next_page = False
    per_page_show = 5
    path=self.request.path
    have_cat = False
    _category_id=0

    if path.startswith('/page'):
      params = path[6:].split('/')
      if len(params)==1:
        page=int(params[0])
      else:
        if len(params)==3 and params[1]=='category':
          have_cat =True
          page=int(params[0])
          _category_id=int(params[2])
      
      
    # print page

    if have_cat:
      _request_cat=Category.get_by_id(_category_id)
      all_blogs=_request_cat.blogs
    else:
      all_blogs = Blog.all()
    max_page = ( all_blogs.count() -1) / per_page_show
    Blogs=all_blogs.order('-date').fetch(per_page_show,offset=page * per_page_show)

    show_prev_page = not (page == 0)
    show_next_page = not (page == max_page)
    show_page_panel = show_prev_page or show_next_page
    
    Categories=Category.all()
    Recent_Blogs=Blog.all().order('-date').fetch(5)    
    
    if Blogs :
      self.template_values={
        'Blogs':Blogs,
        'recent_blogs':Recent_Blogs,
        'show_prev_page':show_prev_page,
        'show_next_page':show_next_page,
        'show_page_panel':show_page_panel,
        'prev_page_num':page-1,
        'next_page_num':page+1,
        'Categories':Categories,
        'is_logined':self.is_login,
        'is_admin':self.is_admin,
        'have_cat':have_cat,
        'category_id':_category_id
        }
      self.render('templates/list_blog.html')
    else:
      self.template_values={
        'recent_blogs': Recent_Blogs,
        'Categories':Categories,
        'msg':'Current no blog'
        }
      self.render('templates/message_blog.html')

class ItemBlog(HelloBlog):
  def get(self):
    url=self.request.path
    _blog_id=url[11:]
    _blog=Blog.get_by_id(int(_blog_id))

    if _blog==None:
      self.write('No such Blog')
    else:
      Categories=Category.all()
      Recent_Blogs=Blog.all().order('-date').fetch(5)

      _comments=_blog.comments

      self.template_values={
        'blog':_blog,
        'comments':_comments,
        'recent_blogs':Recent_Blogs,
        'Categories':Categories,
        }
      self.render('templates/item_blog.html')
    

class RssBlog(HelloBlog):
  def get(self):
    rss_out_count=5
    path=self.request.path

    len_str=len(path)
    #print path
    if len_str==len('/blog/rss'):
      Blogs=Blog.all().order('-date').fetch(rss_out_count)
    else:
      real_path=path[len('/blog/rss')+1:]
      #print real_path
      params=real_path.split('/')
      _category_id=int(params[1])
      _cat=Category.get_by_id(_category_id)
      Blogs=_cat.blogs.fetch(rss_out_count)
      

    blog_items=[]
  
    for _blog in Blogs:
      _blog_url='%s/blog/show/%s' % (self.request.host_url,_blog.key())
      blog_items.append(PyRSS2Gen.RSSItem(
        title = _blog.title,
        author = _blog.author.nickname(),
        link = _blog_url,
        description = _blog.content,
        pubDate = _blog.date,
        guid = PyRSS2Gen.Guid(_blog_url),
        categories = [_blog.category.name]
        )
                        )

    blog_title = 'Hello Blog';
    rss = PyRSS2Gen.RSS2(
      title = blog_title,
      link = self.request.host_url + '/',
      description = 'Lastest %d posts of %s ' % (rss_out_count,blog_title),
      lastBuildDate = datetime.datetime.now(),
      items = blog_items
      )
        
    self.response.headers['Content-type']='application/rss+xml; charset=utf-8'
    self.write_str(rss.to_xml(encoding='utf-8'))

class NewComment(HelloBlog):
  def post(self):
    if self.check_login(users.create_login_url(self.request.uri)):
      _blog_id=self.param('blog_id')
      _detail=urllib.quote_plus(self.param('detail'))
      _blog=Blog.get_by_id(int(_blog_id))

      if _blog==None:
        self.write('Blog not find')
      else:
        try:
          _comment=Comment(
            blog=_blog,
            detail=_detail,
            author=users.get_current_user()
            )
          _comment.put()

          self.redirect('/blog/show/%s' % (_blog_id))
        except db.BadValueError,e:
          self.redirect('/')

  def get(self):
    self.redirect('/')

class AboutMe(HelloBlog):
  def get(self):
    Categories=Category.all()
    Recent_Blogs=Blog.all().order('-date').fetch(5)

    self.template_values={
      'recent_blogs':Recent_Blogs,
      'Categories':Categories,
      }
    self.render('templates/about_me.html')


    
    
def main():
  application = webapp.WSGIApplication([
    ('/', ListBlog),    
    ('/page/\\d+',ListBlog),
    ('/page/\\d+/category/\\d+',ListBlog),
    ('/blog/show/\\d+',ItemBlog),
    ('/blog/aboutme',AboutMe),
    ('/comment/new',NewComment),
    ('/blog/rss',RssBlog),
    ('/blog/rss/category/\\d+',RssBlog)
    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
