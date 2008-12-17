#!/usr/bin/env python #
# -*- coding: UTF-8 -*-

import wsgiref.handlers
import sys
import datetime

sys.path.append('modules')
sys.path.append('models')

from helloblog import *
from blog import *
from category import *
import PyRSS2Gen

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

def main():
  application = webapp.WSGIApplication([  
    ('/blog/rss',RssBlog),
    ('/blog/rss/category/\\d+',RssBlog)
    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()

