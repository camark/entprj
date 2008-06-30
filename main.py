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

class NewBlogHandler(HelloBlog):
  
  def get(self):
    self.response.headers['Content-type']='text/html'
    self.template_values={
      'Categories':Category.all().fetch(1000)
      }
    self.render('templates/new_blog.html')

  def post(self):
    _title=self.param('title')
    _content=db.Text(self.param('content'))
    _category_id=self.param('category_id')
    _category=Category.get(_category_id)
    _blog=Blog(
      title=_title,
      content=_content,
      category=_category
      )
    _blog.put()

    self.redirect('/')

class DeleteBlog(HelloBlog):
  def get(self):
    self.response.headers['Content-type']='text/html'
    self.response.out.write('Delete Blog')

class ListBlog(HelloBlog):
  def get(self):
    Blogs=Blog.all().order('-date')

    if Blogs.count()>0:
      self.template_values={
        'Blogs':Blogs
        }
      self.render('templates/list_blog.html')
    else:
      self.write('Current no blog!')

class ItemBlog(HelloBlog):
  def get(self):
    url=self.request.path
    _blog_id=url[11:]
    _blog=Blog.get(_blog_id)

    _comments=_blog.comments

    self.template_values={
      'blog':_blog,
      'comments':_comments
      }
    self.render('templates/item_blog.html')
    
class NewCategory(HelloBlog):
  def get(self):
    self.render('templates/new_category.html',{})

  def post(self):
    cat_name=self.param('cat_name')

    category=Category(name=cat_name)

    category.put()
    if category.is_saved():
      self.redirect('/')
    else:
      self.write('Save Error!')


class ListCategory(HelloBlog):
  def get(self):
    cats=Category.all().fetch(50)
    self.template_values={
      'Categories':cats
      }
    self.render('templates/list_category.html')

class RssBlog(HelloBlog):
  def get(self):
    count=5
    Blogs=Blog.all().fetch
    self.template_values={
      'blogs':Blogs
      }
    self.response.headers['Content-type']='application/rss+xml; charset=utf-8'
    self.render('templates/rss_blog.html')

class NewComment(HelloBlog):
  def post(self):
    _blog_id=self.param('blog_id')
    _detail=self.param('detail')
    _blog=Blog.get(_blog_id)

    if _blog==None:
      self.write('Blog not find')
    else:
      _comment=Comment(
        blog=_blog,
        detail=_detail
        )
      _comment.put()

      self.redirect('/blog/show/%s' % (_blog_id))
    
def main():
  application = webapp.WSGIApplication([
    ('/', ListBlog),
    ('/blog/new',NewBlogHandler),
    ('/blog/delete',DeleteBlog),
    ('/blog/show/.*',ItemBlog),
    ('/category/new',NewCategory),
    ('/category/list',ListCategory),
    ('/comment/new',NewComment),
    ('/blog/rss',RssBlog)
    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
