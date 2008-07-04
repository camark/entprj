import wsgiref.handlers
import xmlrpclib
import sys
import cgi
from datetime import datetime
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from google.appengine.api import users

sys.path.append('modules')
from helloblog import *
from blog import *
from category import *
from models import *

def check_api_user_pass(username,password):
    user = users.User(username)

    if not user or password != '1234':
        return None

    return user

def metaWeblog_newPost(blogid,username,password,content,publish):
    user = check_api_user_pass(username,password)

    if not user:
        raise Exception, ' access denied'

    if publish:
        if content.has_key('categories'):
            category = Category.all().fetch('name=',content['categories'])
            if not category:
                category = Category.all().fetch(1)
        else:
            category = Category.all().fetch(1)

        _blog=Blog(
            title=content['title'],
            content=content['description'],
            author=user,
            category=category
            )

        key=_blog.put()
        return str(key.id())

def metaWeblog_editPost(blogid,username,password,content,publish):
    user = check_api_user_pass(username,password)

    if not user:
        raise Exception, ' access denied'

    if publish:
        if content.has_key('categories'):
            category = Category.all().fetch('name=',content['categories'])
            if not category:
                category = Category.all().fetch(1)
        else:
            category = Category.all().fetch(1)
            
        _blog=Blog.get_by_id(blogid)

        if not _blog:
            raise Exception,'no such blog by id %s' %(blogid)
        
        _blog.title=content['title']
        _blog.content=content['description'],
        _blog.author=user
        _blog.category=category

        _blog.put()

        return True
    else:
        return True

def metaWeblog_getCategories(blogid, username, password):
    user = check_api_user_pass(username, password)
    if not user:
        raise Exception, 'access denied'

    categories = []
    all_category = Category.all()
    for _cat in all_category:
        categories.append({'description' : _cat.name, 'title' : _cat.name})

    return categories

def metaWeblog_getPost(postid, username, password):
    user = check_api_user_pass(username, password)
    if not user:
            raise Exception, 'access denied'

    _blog = Blog.get_by_id(postid)

    if not_blog:
        raise Exception,'no such blog'
    
    return {
        'postid' : postid,
        'dateCreated' : _blog.date,
        'title' : _blog.title,
        'description' : unicode(_blog.content),
        'categories' : _blog.category.name,
        'publish' : True
        }

def metaWeblog_getRecentPosts(blogid, username, password, numberOfPosts):
    _blogs = Blog.all().order('-date').fetch(min(numberOfPosts,5))

    result = []

    for _blog in _blogs:
        result.append({
            'postid' : postid,
            'dateCreated' : _blog.date,
            'title' : _blog.title,
            'description' : unicode(_blog.content),
            'categories' : _blog.category.name,
            'publish' : True
            }
                      )
    return result


class HelloBlogXMLRPCDispatcher(SimpleXMLRCPDispatcher):
    def __init__(self,funs):
        SimpleXMLRCPDispatcher.__init__(self,True,'utf-8')
        self.funcs=funs
        
dispatcher = HelloBlogXMLRPCDispatcher({
	'metaWeblog.newPost' : metaWeblog_newPost,
	'metaWeblog.editPost' : metaWeblog_editPost,
	'metaWeblog.getCategories' : metaWeblog_getCategories,
	'metaWeblog.getPost' : metaWeblog_getPost,
	'metaWeblog.getRecentPosts' : metaWeblog_getRecentPosts,
	})


# {{{ Handlers
class CallApi(PlogRequestHandler):
	def get(self):
		Logger(request = self.request.uri, response = '----------------------------------').put()
		self.write('<h1>please use POST</h1>')

	def post(self):
		#self.response.headers['Content-Type'] = 'application/xml; charset=utf-8'
		request = self.request.body
		response = dispatcher._marshaled_dispatch(request)
		Logger(request = unicode(request, 'utf-8'), response = unicode(response, 'utf-8')).put()
		self.write(response)
		
def main():
	application = webapp.WSGIApplication(
			[
			    ('/api/xml-rpc', CallApi),
				],
			debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()
