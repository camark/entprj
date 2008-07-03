#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import wsgiref.handlers
import sys
import datetime

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
    Blogs=Blog.all().order('-date')
    Categories=Category.all()
    Recent_Blogs=Blog.all().order('-date').fetch(5)    
    
    if Blogs.count()>0:
      self.template_values={
        'Blogs':Blogs,
        'recent_blogs':Recent_Blogs,
        'Categories':Categories,
        'is_logined':self.is_login,
        'is_admin':self.is_admin
        }
      self.render('templates/list_blog.html')
    else:
      self.write('Current no blog!')

class ItemBlog(HelloBlog):
  def get(self):
    url=self.request.path
    _blog_id=url[11:]
    _blog=Blog.get(_blog_id)
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
    Blogs=Blog.all().order('-date').fetch(rss_out_count)

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
    self.write(rss.to_xml(encoding='utf-8'))

class NewComment(HelloBlog):
  def post(self):
    if self.check_login(users.create_login_url(self.request.uri)):
      _blog_id=self.param('blog_id')
      _detail=self.param('detail')
      _blog=Blog.get(_blog_id)

      if _blog==None:
        self.write('Blog not find')
      else:
        _comment=Comment(
          blog=_blog,
          detail=_detail,
          author=users.get_current_user()
          )
        _comment.put()

        self.redirect('/blog/show/%s' % (_blog_id))

  def get(self):
    self.redirect('/')

class AboutMe(HelloBlog):
  def get(self):
    self.render('templates/about_me.html',{})
    
def main():
  application = webapp.WSGIApplication([
    ('/', ListBlog),
    ('/blog/show/.*',ItemBlog),
    ('/blog/aboutme',AboutMe),
    ('/comment/new',NewComment),
    ('/blog/rss',RssBlog)
    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
